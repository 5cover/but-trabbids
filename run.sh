
#!/usr/bin/env bash
# run the app

set -eu
cd "$(dirname "${BASH_SOURCE[0]}")"
# shellcheck source=venv/bin/activate
. "${1-.venv}"/bin/activate
set -x
if ! find data/processed/ -type d -not -empty; then
    python3 -m src.data_loading;
fi
python3 -m src.dashboard.app
