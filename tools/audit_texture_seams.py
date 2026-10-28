#!/usr/bin/env python3
"""Read-only BSP shared-edge UV audit. Requires NumPy; candidates need review."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct

import numpy as np


def material_images(source):
    """Resolve aliases sharing a diffuse image (including *_planar variants)."""
    images = {}
    for path in (source / 'scripts').glob('*.shader'):
        text = re.sub(r'/\*.*?\*/|//[^\n]*', '', path.read_text(), flags=re.S)
        depth, start, name = 0, 0, ''
        for token in re.finditer(r'[^\s{}]+|[{}]', text):
            value = token[0]
            if value == '{':
                if depth == 0:
                    start = token.end()
                depth += 1
            elif value == '}':
                depth -= 1
                if depth == 0:
                    match = re.search(r'\bdiffuseMap\s+(\S+)', text[start:token.start()])
                    images[name] = match[1] if match else name
            elif depth == 0:
                name = value
    return images


def audit(source, bsp):
    data = bsp.read_bytes()
    if data[:4] != b'IBSP' or struct.unpack_from('<i', data, 4)[0] != 46:
        raise ValueError('Expected an IBSP version 46 map.')
    lumps = [struct.unpack_from('<ii', data, 8 + i * 8) for i in range(17)]

    def read_lump(index, fmt):
        offset, size = lumps[index]
        return list(struct.iter_unpack(fmt, data[offset:offset + size]))

    names = [row[0].split(b'\0')[0].decode() for row in read_lump(1, '<64sii')]
    vertices = np.array(read_lump(10, '<10f4B'))
    indices = np.array([row[0] for row in read_lump(11, '<i')])
    surfaces = read_lump(13, '<12i12f2i')
    images = material_images(source)
    edges, examples = {}, {}
    stats, pairs = Counter(), Counter()
    for surface in surfaces:
        name = names[surface[0]]
        if name.startswith('common/'):
            continue
        verts = vertices[surface[3]:surface[3] + surface[4]]
        triangles = indices[surface[5]:surface[5] + surface[6]].reshape(-1, 3)
        for triangle in triangles:
            points = verts[triangle]
            normal = np.cross(points[1, :3] - points[0, :3],
                              points[2, :3] - points[0, :3])
            length = np.linalg.norm(normal)
            if length < .001:
                continue
            normal /= length
            stats['triangles'] += 1
            for a, b in [(0, 1), (1, 2), (2, 0)]:
                first = tuple(np.round(points[a, :3], 3))
                second = tuple(np.round(points[b, :3], 3))
                if first == second:
                    continue
                key = tuple(sorted((first, second)))
                order = [a, b] if first <= second else [b, a]
                edges.setdefault(key, []).append((name, points[order, 3:5], normal))

    for key, values in edges.items():
        # Exact shared edges only; intersections and T-junctions need another test.
        if len(values) != 2:
            continue
        (a, uv_a, normal_a), (b, uv_b, normal_b) = values
        cosine = float(normal_a @ normal_b)
        if cosine < .9:
            continue
        stats['smooth_shared_edges'] += 1
        same_image = images.get(a, a) == images.get(b, b)
        delta = uv_a - uv_b
        # One constant integer shift repeats the same image along the whole edge.
        jump = float(abs(delta - np.round(delta[0])).max())
        if same_image and jump < .002:
            stats['continuous'] += 1
            continue
        label = 'same_image_uv_jump' if same_image else 'different_material'
        stats[label] += 1
        if cosine > .999847695:  # within one degree
            stats[label + '_nearly_flat'] += 1
        pair = tuple(sorted([a, b]))
        pairs[pair] += 1
        rows = examples.setdefault(pair, [])
        if len(rows) < 5:
            rows.append({'edge': key, 'uv_jump': jump,
                         'angle_degrees': float(np.degrees(np.arccos(np.clip(cosine, -1, 1))))})

    return {
        'bsp_sha256': hashlib.sha256(data).hexdigest(),
        'summary': dict(stats),
        'pairs': [{'materials': pair, 'count': count, 'examples': examples[pair]}
                  for pair, count in pairs.most_common()],
        'used_materials': sorted({names[surface[0]] for surface in surfaces}),
        'method': ('Candidate discontinuities along exactly shared BSP edges within '
                   '25.84 degrees. UV tolerance .002 repeats. Nearly-flat threshold '
                   '1 degree. Includes hidden faces and intentional atlas/trim seams; '
                   'not a visual defect count. T-junction-only and intersecting seams '
                   'may be missed. Sky cubemap image seams are outside this test.'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--bsp', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.source, args.bsp)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'seam-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
