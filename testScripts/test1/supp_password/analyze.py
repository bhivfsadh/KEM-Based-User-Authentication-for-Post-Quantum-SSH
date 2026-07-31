#!/usr/bin/env python3
# analyze_test6.py — Exp 6: Password authentication baseline results
#
# Read raw timings from password_raw.csv, compute p50/p95/mean,
# output the Password--yescrypt row for appending to the paper's Table III.
#
# Usage:
#   python3 analyze_test6.py <raw_csv> <summary_csv> [output_md]

import sys
import csv
import os
from statistics import median


def load_raw(csv_path: str) -> list:
    """Load raw timing CSV."""
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def analyze(rows: list) -> dict:
    """Group by auth_method, compute p50/p95/mean."""
    from collections import defaultdict
    groups = defaultdict(list)
    for row in rows:
        lt = row.get('latency_ms', 'NA')
        method = row.get('auth_method', 'unknown')
        if lt != 'NA':
            groups[method].append(float(lt))

    results = {}
    for method, lats in groups.items():
        lats.sort()
        n = len(lats)
        results[method] = {
            'count': n,
            'p50': lats[int(n * 0.50)],
            'p95': lats[min(int(n * 0.95), n - 1)],
            'mean': sum(lats) / n,
        }
    return results


def fmt(val, template='.2f', na='—'):
    if val is None:
        return na
    return f'{val:{template}}'


def generate_markdown(results: dict, rtt_ms: int = 67) -> str:
    """Generate Markdown report."""
    lines = []
    lines.append('# Exp 6: Password Authentication + Ed25519 Baseline')
    lines.append('')
    lines.append(f'Fixed conditions: RTT={rtt_ms}ms, KEX=mlkem768x25519-sha256, hostkey=ssh-ed25519')
    lines.append('')
    lines.append('| Authentication Method | Connections | p50 (ms) | p95 (ms) | mean (ms) |')
    lines.append('|:---|---:|---:|---:|---:|')

    for method in sorted(results.keys()):
        r = results[method]
        label = {'password': 'Password (yescrypt)', 'ed25519': 'Ed25519 (pubkey)',
                 'mldsa65': 'ML-DSA-65 (pubkey)', 'kem': 'ML-KEM-768 (KEM)'}.get(method, method)
        lines.append(
            f'| {label} | {r["count"]} | '
            f'{fmt(r["p50"])} | {fmt(r["p95"])} | {fmt(r["mean"])} |'
        )
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 analyze_test6.py <raw_csv> <summary_csv> [output_md]")
        sys.exit(1)

    raw_csv = sys.argv[1]
    summary_csv = sys.argv[2]
    output_md = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(raw_csv):
        print(f"[ERR] raw CSV not found: {raw_csv}")
        sys.exit(1)

    rows = load_raw(raw_csv)
    results = analyze(rows)

    if not results:
        print("No valid measurements")
        sys.exit(1)

    # Write summary CSV
    with open(summary_csv, 'w') as f:
        f.write('auth_method,total,p50_ms,p95_ms,mean_ms\n')
        for method in sorted(results.keys()):
            r = results[method]
            f.write(f'{method},{r["count"]},{fmt(r["p50"], ".2f")},{fmt(r["p95"], ".2f")},{fmt(r["mean"], ".2f")}\n')

    for method in sorted(results.keys()):
        r = results[method]
        print(f'{method}: n={r["count"]} p50={r["p50"]:.2f}ms p95={r["p95"]:.2f}ms mean={r["mean"]:.2f}ms')

    if output_md:
        md_content = generate_markdown(results)
        with open(output_md, 'w') as f:
            f.write(md_content)
        print(f'Report written to {output_md}')


if __name__ == '__main__':
    main()
