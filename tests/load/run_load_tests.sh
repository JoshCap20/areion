#!/bin/bash

set -e

cd "$(dirname "$0")/../.."

if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

pip install -e .

python tests/load/test_server.py &
SERVER_PID=$!

cleanup() {
    echo "Stopping server..."
    kill $SERVER_PID
}

trap cleanup EXIT

sleep 2

mkdir -p tests/load/load_test_results

endpoints=(
    "json"
    "plaintext"
)

configs=(
    "-t12 -c400 -d30s"
    "-t8 -c200 -d20s"
    "-t4 -c100 -d10s"
)

for endpoint in "${endpoints[@]}"; do
    for config in "${configs[@]}"; do
        filename="load_test_${endpoint}_$(echo $config | tr ' -' '_').txt"
        echo "Running wrk $config on /$endpoint"
        wrk $config http://localhost:8080/$endpoint > tests/load/load_test_results/$filename
    done
done

echo "Aggregating results into load_test_results/combined_results.txt"
cat tests/load/load_test_results/load_test_*.txt > tests/load/load_test_results/combined_results.txt
