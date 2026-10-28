# Exercise cycle collision repair

The three current bikes are scaled to 0.5, with origins at (-411, -1818,
31.9464), (-514, -1818, 31.9464) and (-617, -1818, 31.9464). Their old
full-size collision remained around X=-306, -512 and -718 at Y=-1814.

Removed 54 stale world brushes, including three coarse placeholders. Replaced
these with 14 fitted convex pieces per bike: 42 common/fullclip detail brushes
in the exercise_cycle_collision generated group. Curved frame and handlebar
pieces are split into slabs to preserve the openings. Each piece uses 26
support planes and 0.2 local units of outer allowance (0.1 at current scale).
The model, transforms, visible brushes, materials and UVs are unchanged.

`local-hulls.json` stores the reusable local support planes; `parts.json`
records the connected component/slab bounds. The removed brushes are recorded
by digest and bounds for review. After moving/scaling bikes, save the map and
run from the source package root:

    python3 tools/rebuild_exercise_cycle_collision.py

Then reload the map in NetRadiant. The helper replaces only its generated group.
It requires NumPy and currently supports yaw in angle, not pitch/roll in angles.

The compiled collision check covers 9,488 surface samples per instance, confirms
human-sized passage between both pairs of bikes, and tests the obsolete upper
hull positions. It also verifies all model properties and all nonremoved brush
text/UVs against the checkpoint. The diagnostic leak/BSP compile is clean.

The production BSP, lighting and navigation were not overwritten. Rebuild the
map before in-game review. Your manual map edits were checkpointed separately
in e0b0ba9 before this repair.
