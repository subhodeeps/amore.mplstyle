#!/usr/bin/env bash
# Check the amore repository: Python, LaTeX, a virtual environment, and the tests.
#
#   scripts/check.sh              install into .venv (once) and run the tests
#   scripts/check.sh --examples   also regenerate the example figures in docs/figures/
#
# Set PYTHON=/path/to/python3 to choose the interpreter. The steps are the same as the manual
# steps in README.md ("Check that it works").
set -euo pipefail
cd "$(dirname "$0")/.."

with_examples=0
[ "${1:-}" = "--examples" ] && with_examples=1

say() { printf '[check] %s\n' "$*"; }

py="${PYTHON:-python3}"
command -v "$py" >/dev/null 2>&1 || { say "no Python interpreter found (tried $py)"; exit 127; }
"$py" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || { say "Python 3.10 or newer is needed; found $("$py" --version 2>&1)"; exit 1; }
say "python: $("$py" --version 2>&1)"

# LaTeX is needed to draw text in the amore style. The tests that draw a figure skip without it.
if command -v latex >/dev/null 2>&1 && command -v dvipng >/dev/null 2>&1; then
  say "LaTeX: latex and dvipng found"
else
  say "LaTeX: latex or dvipng is missing. The tests that draw a figure will SKIP (a skip is not a pass)."
  [ "$with_examples" = 1 ] && { say "the examples need LaTeX; install it first"; exit 1; }
fi

if [ ! -d .venv ]; then
  say "creating .venv"
  "$py" -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
extras="test"
[ "$with_examples" = 1 ] && extras="test,examples"
say "installing amore with the extras: $extras"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -e ".[${extras}]"

say "running the tests"
python -m pytest -q -rs

if [ "$with_examples" = 1 ]; then
  say "regenerating the example figures (about 40 s)"
  python -m amore.examples
  ls -1 docs/figures/*.png
fi
say "done: all checks passed"
