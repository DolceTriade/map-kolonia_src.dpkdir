#!/usr/bin/env python3
"""Package an already compiled kolonia dpkdir. Requires Pillow and crunch."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
from PIL import Image, features

RASTER = {'.png', '.tga', '.jpg', '.jpeg', '.webp', '.bmp'}
# Same basename preference as this project's Daemon image loader.
PRIORITY = ['.webp', '.png', '.tga', '.jpg', '.jpeg', '.bmp', '.dds', '.crn', '.ktx']
SCRATCH = {'.prt', '.lin', '.srf', '.bak', '.tmp', '.log', '.dpk', '.pk3', '.pyc'}
AUTHORING = {'.map', '.obj', '.mtl', '.blend', '.psd', '.xcf', '.py', '.sh', '.ps1', '.bat'}
EXCLUDED_DIRS = {'build', '__pycache__', 'tools', 'devassets'}
# Both Quake and native OpenGL cubemap faces need lossless edges to avoid seams.
SKY_FACE_SUFFIXES = ('_bk', '_dn', '_ft', '_lf', '_rt', '_up',
                     '_px', '_nx', '_py', '_ny', '_pz', '_nz')
# Low-detail assets reviewed individually. Keep detailed rock scans and the
# 4K amber normal/glow/physical maps at their authored resolution.
RESIZE_LIMITS = {
    f'textures/kolonia/{stem}_{channel}': 512
    for stem in ('bark', 'foliage') for channel in ('d', 'n', 'p')
}
RESIZE_LIMITS.update({
    f'textures/kolonia/ship_light_{channel}': 512
    for channel in ('d', 'n', 'p', 'g')
})


def fail(message):
    raise SystemExit(message)


def available_cpus():
    # Respect task affinity (containers/cpusets) where the platform exposes it.
    process_count = getattr(os, 'process_cpu_count', None)
    if process_count:
        return process_count() or 1
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count() or 1


def shader_map_paths(source, keyword):
    """Collect simple material map paths; naming conventions remain a fallback."""
    paths = set()
    for shader in (source / 'scripts').rglob('*.shader'):
        text = re.sub(r'/\*.*?\*/|//[^\n]*', '', shader.read_text(), flags=re.S)
        for match in re.finditer(rf'(?im)^\s*{keyword}\s+([^\s{{}}]+)', text):
            path = Path(match[1].strip('"'))
            if path.suffix.lower() in PRIORITY:
                path = path.with_suffix('')
            paths.add(path.as_posix().lower())
    return paths


def shader_normal_maps(source):
    return shader_map_paths(source, "normalMap")


def is_normal_map(rel, shader_paths):
    return (rel.with_suffix('').as_posix().lower() in shader_paths
            or rel.stem.lower().endswith(('_n', '_norm', '_normal')))


def resized_image(image, rel, lossless, enabled):
    """Return an optional package-only image copy and a reason for resizing."""
    if not enabled or lossless or rel.parts[0].lower() != 'textures':
        return None, None
    # A uniform RGBA image has no spatial information to lose. Keep a 4x4
    # block so all CRN/DXT formats, including DXN normals, can encode it.
    if all(low == high for low, high in image.getextrema()):
        if image.size != (4, 4):
            return image.resize((4, 4), Image.Resampling.NEAREST), 'uniform'
        return None, None
    limit = RESIZE_LIMITS.get(rel.with_suffix('').as_posix().lower())
    if limit and max(image.size) > limit:
        ratio = limit / max(image.size)
        size = tuple(max(1, round(dimension * ratio)) for dimension in image.size)
        # Normal and physical maps are channel data: Pillow filters the stored
        # channels directly; crunch subsequently renormalizes DXN normals.
        return image.resize(size, Image.Resampling.LANCZOS), 'reviewed'
    return None, None


def convert_file(task):
    rel, path, stage, temporary, crunch, helpers, keep_sources, normal_map, physical_map, resize = task
    ext = rel.suffix.lower()
    target = rel
    action = 'copy'
    if ext in RASTER:
        lossless = ((rel.parts[0] == 'maps' and rel.name.startswith('lm_'))
                    or rel.stem.lower().endswith(SKY_FACE_SUFFIXES)
                    # Preserve the amber tile pattern and its normal/physical
                    # channels exactly; CRN compression produces visible artifacts.
                    or (rel.parent.as_posix().lower() == 'textures/kolonia'
                        and rel.stem.lower().startswith('amber_')))
        target = rel.with_suffix('.webp' if lossless else '.crn')
        action = 'lossless-webp' if lossless else 'crunch'
        dst = stage / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(path) as original:
            with original.convert('RGBA' if 'A' in original.getbands() or 'transparency' in original.info else 'RGB') as image:
                resized, resize_reason = resized_image(image, rel, lossless, resize)
                render = resized if resized is not None else image
                if resized is not None:
                    action += f'-resized-{image.width}x{image.height}-to-{render.width}x{render.height}-{resize_reason}'
                if lossless:
                    render.save(dst, 'WEBP', lossless=True, quality=100, method=6, exact=True)
                else:
                    # Each process owns its transient file; concurrent conversions
                    # must never share the old input.tga path.
                    with tempfile.TemporaryDirectory(prefix='image-', dir=temporary) as image_work:
                        tga = Path(image_work) / 'input.tga'
                        render.save(tga, 'TGA')
                        cmd = [crunch, '-helperThreads', str(helpers), '-noNormalDetection', '-file', str(tga)]
                        if normal_map:
                            # Vector data must be filtered linearly, not as sRGB.
                            cmd += ['-dxn', '-gamma', '1.0', '-renormalize', '-rtopmip']
                            if rel.parts[0].lower() == 'textures':
                                cmd += ['-wrap']
                        if physical_map and not normal_map:
                            # ORM channels are linear masks, never sRGB colors.
                            cmd += ['-gamma', '1.0']
                        cmd += ['-quality', '255', '-out', str(dst)]
                        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                        if result.returncode or not dst.is_file() or not dst.stat().st_size:
                            raise RuntimeError(f'Image conversion failed: {rel}\n{result.stdout}')
                if resized is not None:
                    resized.close()
        if keep_sources:
            original = stage / 'devassets/source-images' / rel
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, original)
    else:
        dst = stage / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dst)
    if normal_map and action.startswith('crunch'):
        action = action.replace('crunch', 'crunch-dxn', 1)
    return {'source':str(rel), 'packaged':str(target), 'action':action}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--version', required=True, help='DPK version, e.g. alpha2 or alpha2.1')
    parser.add_argument('--output-dir', type=Path, default=Path.cwd())
    parser.add_argument('--crunch', default='crunch')
    parser.add_argument('--threads', type=int, default=available_cpus(), help='Total CPU budget (default: all available CPUs)')
    parser.add_argument('--jobs', type=int, help='Concurrent file workers (default: CPU budget); fewer jobs give crunch more helper threads')
    parser.add_argument('--navmesh-dir', type=Path, help='Optional engine-generated navmeshes to include')
    parser.add_argument('--include-source-images', action='store_true', help='Also keep original images under devassets/source-images/')
    parser.add_argument('--no-resize', action='store_true', help='Keep all packaged images at their original dimensions')
    args = parser.parse_args()
    source = args.source.resolve()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.+-]*', args.version):
        fail('Version must contain letters, digits, dots, plus or hyphens (no underscores).')
    if args.threads < 1 or (args.jobs is not None and args.jobs < 1):
        fail('--threads and --jobs must be positive.')
    if not source.is_dir() or not (source / 'maps/kolonia.bsp').is_file():
        fail('Source must contain maps/kolonia.bsp; compile it in Radiant first.')
    if not (source / 'maps/kolonia.map').is_file() or not (source / 'DEPS').is_file():
        fail('Source must contain maps/kolonia.map and DEPS.')
    if not list((source / 'maps/kolonia').glob('lm_*')):
        fail('External lightmaps are missing from maps/kolonia/.')
    crunch = shutil.which(args.crunch)
    if not crunch:
        fail('crunch not found; install DaemonEngine/crunch or pass --crunch /path/to/crunch.')
    if not features.check('webp'):
        fail('Pillow needs WebP support for lossless lightmap, skybox and amber conversion.')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir.resolve() / f'map-kolonia_{args.version}.dpk'
    if output.exists():
        fail(f'Refusing to overwrite {output}; use a new version or remove it yourself.')
    normal_maps = shader_normal_maps(source)
    physical_maps = shader_map_paths(source, "physicalMap")
    files = {}
    for path in sorted(source.rglob('*')):
        rel = path.relative_to(source)
        if any(part.startswith('.') or part.lower() in EXCLUDED_DIRS for part in rel.parts):
            continue
        if (path.suffix.lower() in AUTHORING
                or re.fullmatch(r'\.blend\d+', path.suffix.lower())
                or path.name.lower() == 'package-manifest.json'):
            continue
        if path.is_symlink():
            fail(f'Symlink requires review before packaging: {rel}')
        if not path.is_file() or path.suffix.lower() in SCRATCH or 'autosave' in path.name.lower() or path.name.endswith('~'):
            continue
        if path.resolve() == output:
            continue
        files[rel] = path
    # Match the engine's image preference when several source formats share a name.
    images = {}
    for rel in files:
        if rel.suffix.lower() in PRIORITY:
            images.setdefault(rel.with_suffix(''), []).append(rel)
    selected = set()
    for stem, candidates in images.items():
        chosen = min(candidates, key=lambda p: PRIORITY.index(p.suffix.lower()))
        selected.add(chosen)
        if len(candidates) > 1:
            print(f'Image preference: {chosen}')
    with tempfile.TemporaryDirectory(prefix='kolonia-package-') as temporary:
        stage = Path(temporary) / 'stage'
        stage.mkdir()
        tasks = []
        # Resolve aliases before launching workers, ensuring one writer per target.
        for rel, path in files.items():
            if rel.suffix.lower() in PRIORITY and rel not in selected:
                if args.include_source_images:
                    dst = stage / 'devassets/source-images' / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, dst)
                continue
            tasks.append((rel, path))
        # Start larger images first to reduce the long tail of a conversion batch.
        tasks.sort(key=lambda item: (item[0].suffix.lower() in RASTER, item[1].stat().st_size), reverse=True)
        jobs = min(args.jobs or args.threads, args.threads, len(tasks))
        helpers = min(16, max(0, args.threads // max(1, jobs) - 1))
        print(f'CPU budget: {args.threads}; workers: {jobs}; crunch helpers per worker: {helpers}', flush=True)
        with ProcessPoolExecutor(max_workers=max(1, jobs)) as pool:
            futures = [pool.submit(convert_file, (rel, path, stage, temporary, crunch, helpers, args.include_source_images, is_normal_map(rel, normal_maps), rel.with_suffix('').as_posix().lower() in physical_maps, not args.no_resize)) for rel, path in tasks]
            try:
                for future in as_completed(futures):
                    entry = future.result()
                    print(f"{entry['action']}: {entry['source']} -> {entry['packaged']}", flush=True)
            except BaseException:
                # Cancel queued work and wait for active workers before temporary
                # files are cleaned up. No archive is published after a failure.
                for future in futures:
                    future.cancel()
                raise
        if args.navmesh_dir:
            meshes = sorted(args.navmesh_dir.glob('kolonia-*.navMesh'))
            if not meshes:
                fail('No kolonia-*.navMesh files in --navmesh-dir.')
            for path in meshes:
                shutil.copyfile(path, stage / 'maps' / path.name)
        if not list((stage / 'maps').glob('kolonia-*.navMesh')):
            print('NOTE: no navmeshes included. Use --navmesh-dir to ship existing engine-generated navmeshes.')
        # Write beside final output; publish only when the complete archive exists.
        fd, temporary_zip = tempfile.mkstemp(prefix=output.name+'.', suffix='.tmp', dir=output.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(temporary_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for path in sorted(stage.rglob('*')):
                    if path.is_file():
                        # CRN/WebP/DDS/KTX already contain compressed data.
                        # Avoid serial DEFLATE work for these entries.
                        method = zipfile.ZIP_STORED if path.suffix.lower() in {'.crn', '.webp', '.dds', '.ktx', '.jpg', '.jpeg', '.png', '.opus', '.ogg'} else zipfile.ZIP_DEFLATED
                        archive.write(path, path.relative_to(stage).as_posix(), compress_type=method)
            # Hard link publishes atomically and never replaces an existing release.
            os.link(temporary_zip, output)
        finally:
            Path(temporary_zip).unlink(missing_ok=True)
    print(f'Created {output} ({output.stat().st_size / 1048576:.1f} MiB)')


if __name__ == '__main__':
    main()
