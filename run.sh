
#!/usr/bin/env bash
# run the app

set -eu
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ $OS = 'Windows_NT' ]]; then python='py'; else python='python3'; fi
data=data/processed
if ! [[ -d $data && -n "$(ls -A $data)" ]]; then
    $python -m src.data_loading;
fi
$python -m src.dashboard.app
