# World tooling

Tools to keep the SDF world files under [`../../worlds/`](../../worlds/)
consistent and valid. The structure convention itself is documented in
[`../../docs/world-structure.md`](../../docs/world-structure.md):

```
1. PHYSICS & GPS COORDINATE   physics, gravity, magnetic_field, atmosphere, wind, spherical_coordinates
2. ENVIRONMENT & LIGHT        scene, light(s)
3. WORLD MODELS               ground_plane, include, model...
```

| Script | Purpose |
|--------|---------|
| [`world_format.py`](./world_format.py) | Reorder a world's top-level `<world>` children into the 3-section layout and insert section banners — **without changing any element's content**. |
| [`verify_worlds.sh`](./verify_worlds.sh) | Verify a world: structure convention + `gz sdf` parse + headless `gz sim` load. |

## `world_format.py`

```bash
cd Tools/simulation/gz

python3 tools/worlds/world_format.py --all          # format every worlds/*.sdf in place
python3 tools/worlds/world_format.py uwb default     # specific worlds (bare names ok)
python3 tools/worlds/world_format.py --all --check   # report only; exit 1 if not normalized (CI)
```

Safety: each run self-checks that the output is well-formed XML and that the
multiset of world elements is unchanged (nothing added, removed or altered). The
formatter is **idempotent** — running it on an already-formatted file is a no-op.

## `verify_worlds.sh`

```bash
cd Tools/simulation/gz

./tools/worlds/verify_worlds.sh --all        # verify every world
./tools/worlds/verify_worlds.sh uwb          # one world (bare name or path)
ITERS=20 ./tools/worlds/verify_worlds.sh uwb # override gz sim load iterations (default 10)
```

It sets `GZ_SIM_RESOURCE_PATH` automatically and exits non-zero if any world
fails any stage. `gz sdf` cannot resolve `model://` URIs on its own, so those
messages are filtered out — the `gz sim` load is the authoritative check.
