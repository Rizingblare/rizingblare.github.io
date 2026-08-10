#!/usr/bin/env sh
# The one gate. One command, one exit code, whole-repository scan.
#
# Every procedure that produces an artifact names THIS command immediately before
# its commit step, with the failure branch spelled out. That wiring — not this
# script — is what makes the check catalogue mean anything: a check nobody runs at
# a defined moment is documentation.
#
# Keep verification, reading the output, and committing as three separate acts.
# Chaining them into one command looks like a gate and is not one.
#
#   sh scripts/check.sh            development: worktree-clean demoted to a warning
#   sh scripts/check.sh --strict   release gate: a dirty tree fails
#
# worktree-clean is demoted by default because the tree is dirty by definition at
# the moment you run this. Do not delete the check, and do not move the whole gate
# to after the commit — the release form below is where it runs at full severity.
#
# PYTHONPATH is set so that `--plugin your_module:PLUGIN` resolves. The engine also
# imports its own siblings by bare name, which is why it is invoked by path.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/harness_manifest.py" fixtures --root "$ROOT/scripts/fixtures/harness-manifest"
python3 "$ROOT/scripts/harness_manifest.py" lint --root "$ROOT"
python3 "$ROOT/scripts/event_check.py" --fixtures "$ROOT/scripts/fixtures/event-check"
node "$ROOT/scripts/search-query-runtime-check.mjs"
python3 "$ROOT/scripts/public_surface_check.py"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/engine/validate.py" \
  --root "$ROOT" --registry "$ROOT/schema/kernel/layout.yaml" \
  --plugin scripts.event_check:PLUGIN \
  --warn worktree-clean "$@"
