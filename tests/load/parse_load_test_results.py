import re
import os
import pandas as pd

def parse_wrk_output(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    req_per_sec = re.search(r"Requests/sec:\s+([\d\.]+)", content)
    avg_latency = re.search(r"Latency\s+([\d\.]+)([a-zµ]+)", content)
    transfer_per_sec = re.search(r"Transfer/sec:\s+([\d\.]+\w+)", content)

    return {
        'Requests/sec': float(req_per_sec.group(1)) if req_per_sec else None,
        'Avg Latency': avg_latency.group(1) + avg_latency.group(2) if avg_latency else None,
        'Transfer/sec': transfer_per_sec.group(1) if transfer_per_sec else None
    }

def main():
    results_dir = os.path.join(os.getcwd(), 'tests', 'load', 'load_test_results')
    summary = []

    for filename in os.listdir(results_dir):
        if filename.startswith('load_test_') and filename.endswith('.txt'):
            file_path = os.path.join(results_dir, filename)

            parts = filename.rstrip('.txt').split('_')
            endpoint = parts[2]
            config_str = '_'.join(parts[3:])
            config = config_str.replace('_', ' ')

            data = parse_wrk_output(file_path)
            data['Endpoint'] = endpoint
            data['Config'] = config
            summary.append(data)

    df = pd.DataFrame(summary)
    df = df[['Endpoint', 'Config', 'Requests/sec', 'Avg Latency', 'Transfer/sec']]
    df.to_csv(os.path.join(results_dir, 'summary.csv'), index=False)
    df.to_markdown(os.path.join(results_dir, 'summary.md'), index=False)

if __name__ == '__main__':
    main()
