#!/usr/bin/env bash
# Verify Gazebo world files: structure convention + SDF parse + headless load.
#
# Usage:
#   verify_worlds.sh --all              # verify every worlds/*.sdf
#   verify_worlds.sh uwb default        # verify worlds/uwb.sdf, worlds/default.sdf
#   verify_worlds.sh worlds/uwb.sdf     # explicit path also works
#
# Env:
#   ITERS   number of gz sim iterations for the load test (default 10)
#
# Exit code is non-zero if any world fails any stage.
set -uo pipefail

# this script lives in tools/worlds/ ; the gz root is two levels up
GZ_DIR=$(cd "$(dirname "$0")/../.." && pwd)
WORLDS_DIR="$GZ_DIR/worlds"
FMT="$GZ_DIR/tools/worlds/world_format.py"
ITERS="${ITERS:-10}"

export GZ_SIM_RESOURCE_PATH="$GZ_DIR/models:$GZ_DIR/worlds:${GZ_SIM_RESOURCE_PATH:-}"
export IGN_GAZEBO_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH"

if ! command -v gz >/dev/null 2>&1; then
  echo "error: 'gz' not found on PATH" >&2
  exit 2
fi

# ---- collect targets -------------------------------------------------------
declare -a TARGETS
if [ "$#" -eq 0 ] || [ "${1:-}" = "--all" ]; then
  for f in "$WORLDS_DIR"/*.sdf; do TARGETS+=("$f"); done
else
  for a in "$@"; do
    if [ -f "$a" ]; then TARGETS+=("$a")
    elif [ -f "$WORLDS_DIR/$a" ]; then TARGETS+=("$WORLDS_DIR/$a")
    elif [ -f "$WORLDS_DIR/$a.sdf" ]; then TARGETS+=("$WORLDS_DIR/$a.sdf")
    else echo "MISSING  $a"; TARGETS+=("__missing__:$a"); fi
  done
fi

# noise from `gz sdf`/`gz sim` that does not indicate a real problem
IGNORE='findFile|callback|Unable to find uri|EGL|libEGL|gbm|render engine|Sensors|already registered|GUI|Qt|xcb|offscreen'

fail=0
for t in "${TARGETS[@]}"; do
  if [[ "$t" == __missing__:* ]]; then fail=1; continue; fi
  name=$(basename "$t")
  status="OK"
  detail=""

  # 1. structure convention
  if ! "$FMT" --check "$t" >/dev/null 2>&1; then
    status="FAIL"; detail="structure (run: tools/worlds/world_format.py $name)"
  fi

  # 2. SDF parse
  if [ "$status" = "OK" ]; then
    perr=$(gz sdf -k "$t" 2>&1 | grep -iE "error" | grep -vE "$IGNORE")
    [ -n "$perr" ] && { status="FAIL"; detail="sdf parse: $(echo "$perr" | head -1)"; }
  fi

  # 3. headless load
  if [ "$status" = "OK" ]; then
    lerr=$(timeout 60 gz sim -s -r --iterations "$ITERS" "$t" 2>&1 \
            | grep -iE "error|exception|unable to find|malformed" | grep -vE "$IGNORE")
    [ -n "$lerr" ] && { status="FAIL"; detail="load: $(echo "$lerr" | head -1)"; }
  fi

  if [ "$status" = "OK" ]; then
    printf "OK    %-24s\n" "$name"
  else
    printf "FAIL  %-24s %s\n" "$name" "$detail"
    fail=1
  fi
done

exit $fail
