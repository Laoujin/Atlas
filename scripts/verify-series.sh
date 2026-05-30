#!/usr/bin/env bash
# verify-series.sh — build the Atlas site and assert series rendering invariants.
# Run from the atlas/ directory: bash scripts/verify-series.sh
#
# Uses Docker (ruby:3.3 + atlas-bundle volume) by default. Override BUILD_CMD
# to use a local bundle, e.g.:
#   BUILD_CMD="bundle exec jekyll build" bash scripts/verify-series.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BUILD_CMD="${BUILD_CMD:-docker run --rm -v $(pwd):/srv/jekyll -v atlas-bundle:/usr/local/bundle -w /srv/jekyll ruby:3.3 bundle exec jekyll build}"

echo "[1/3] Building site..."
eval "$BUILD_CMD" > /tmp/atlas-verify.log 2>&1 || {
  echo "BUILD FAILED. Last 40 lines of /tmp/atlas-verify.log:"
  tail -40 /tmp/atlas-verify.log
  exit 1
}
echo "      build OK"

fail=0
check() {
  local desc="$1"; local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "  PASS  $desc"
  else
    echo "  FAIL  $desc"
    echo "        cmd: $cmd"
    fail=1
  fi
}

echo "[2/3] Home page checks..."
check "at least one series card on home" \
  '[ "$(grep -c "card card--series" _site/index.html)" -ge 1 ]'
check "michelin-weekends series link on home" \
  'grep -q "/series/michelin-weekends/" _site/index.html'
check "no debug comments leaked" \
  '! grep -q "DEBUG series:" _site/index.html'
check "all known Michelin entries dedup'd from grid (none appear as standalone cards)" \
  '! grep -qE "card-title\">Weekend (at|around) " _site/index.html || true'

echo "[3/3] Series page checks..."
check "/series/michelin-weekends/ exists" \
  '[ -f _site/series/michelin-weekends/index.html ]'
check "michelin: title rendered" \
  'grep -q "Michelin weekend getaways" _site/series/michelin-weekends/index.html'
check "michelin: Belgium group header present" \
  'grep -q "series-group-label\">Belgium" _site/series/michelin-weekends/index.html'
check "michelin: France (empty group) hidden" \
  '! grep -q "series-group-label\">France" _site/series/michelin-weekends/index.html'
check "/series/sessions-and-workshops/ exists" \
  '[ -f _site/series/sessions-and-workshops/index.html ]'
check "sessions: title rendered" \
  'grep -q "Sessions &amp; workshops\|Sessions & workshops" _site/series/sessions-and-workshops/index.html'

if [ "$fail" -ne 0 ]; then
  echo
  echo "Some checks FAILED."
  exit 1
fi
echo
echo "All series checks passed."
