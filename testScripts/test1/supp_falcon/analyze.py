#!/usr/bin/env python3
# analyze_test5.py — Exp 5: FN-DSA baseline augmentation results
#
# Read raw timings from falcon_raw.csv, compute p50/p95/mean,
# output results that can be appended to the paper's Table III.
#
# Usage:
#   python3 analyze_test5.py <raw_csv> <summary_csv> [output_md]

import sys
import csv
import os
from collections import defaultdict
from statistics import median


def load_raw(csv_path: str) -> list:
    """Load raw timing CSV."""
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def aggregate(rows: list) -> dict:
    """Group by algorithm, compute p50/p95/mean."""
    groups = defaultdict(list)
    for row in rows:
        lt = row.get('latency_ms', 'NA')
        if lt != 'NA':
            groups[row['alg']].append(float(lt))

    result = {}
    for alg in sorted(groups.keys()):
        lats = sorted(groups[alg])
        n = len(lats)
        if n == 0:
            continue
        result[alg] = {
            'count': n,
            'p50': lats[int(n * 0.50)],
            'p95': lats[min(int(n * 0.95), n - 1)],
            'mean': sum(lats) / n,
        }
    return result


def fmt(val, template='.2f', na='—'):
    if val is None:
        return na
    return f'{val:{template}}'


def generate_markdown(agg: dict, rtt_ms: int = 67) -> str:
    """Generate Markdown table that can be appended to the paper's Table III."""
    lines = []
    lines.append('# Exp 5: FN-DSA Baseline Augmentation (Falcon-512 / Falcon-1024)')
    lines.append('')
    lines.append(f'Fixed conditions: RTT={rtt_ms}ms, KEX=mlkem768x25519-sha256, hostkey=ssh-ed25519')
    lines.append('')
    lines.append('| Algorithm | Connections | p50 (ms) | p95 (ms) | mean (ms) |')
    lines.append('|:---|---:|---:|---:|---:|')

    for alg in sorted(agg.keys()):
        d = agg[alg]
        lines.append(
            f'| {alg} | {d["count"]} | {fmt(d["p50"])} | {fmt(d["p95"])} | {fmt(d["mean"])} |'
        )

    lines.append('')
    lines.append('> The table above can be directly appended to the paper\'s Table III (Figure 3).')
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 analyze_test5.py <raw_csv> <summary_csv> [output_md]")
        sys.exit(1)

    raw_csv = sys.argv[1]
    summary_csv = sys.argv[2]
    output_md = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(raw_csv):
        print(f"[ERR] raw CSV not found: {raw_csv}")
        sys.exit(1)

    rows = load_raw(raw_csv)
    agg = aggregate(rows)

    # Write summary CSV
    with open(summary_csv, 'w') as f:
        f.write('alg,total,successes,p50_ms,p95_ms,mean_ms\n')
        for alg in sorted(agg.keys()):
            d = agg[alg]
            f.write(f'{alg},{d["count"]},{d["count"]},{d["p50"]:.2f},{d["p95"]:.2f},{d["mean"]:.2f}\n')

    print(f'Summary written to {summary_csv}')
    for alg in sorted(agg.keys()):
        d = agg[alg]
        print(f'  {alg}: n={d["count"]} p50={d["p50"]:.2f}ms p95={d["p95"]:.2f}ms mean={d["mean"]:.2f}ms')

    # Generate Markdown report
    if output_md:
        md_content = generate_markdown(agg)
        with open(output_md, 'w') as f:
            f.write(md_content)
        print(f'Report written to {output_md}')


if __name__ == '__main__':
    main()
