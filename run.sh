#!/usr/bin/env bash
# run the app

set -eu
cd "$(dirname "${BASH_SOURCE[0]}")"
. venv/bin/activate
set -x
if ! find data/processed/ -type d -not -empty; then
    python3 -m src.raph.rendements_journaliers;
    python3 -m src.data_loading;
    python3 -m src.mato.stats_descriptives;
fi
python3 -m src.dashboard.app
