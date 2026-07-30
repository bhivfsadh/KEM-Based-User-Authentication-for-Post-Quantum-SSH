#!/usr/bin/env python3
# analyze_test3.py — Experiment 3 result analysis
#
# Summarizes protocol-level data and parses local decaps output.
#
# Usage:
#   python3 analyze_test3.py protocol <raw_csv> <summary_csv> [output_md]
#   python3 analyze_test3.py local <output_txt> [output_md]

import sys
import csv
import os
from collections import defaultdict
from statistics import median

def analyze_protocol(raw_csv: str, summary_csv: str, output_md: str = None):
    """Analyze protocol-level test data."""
    rows = []
    with open(raw_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    groups = defaultdict(list)
    for row in rows:
        groups[row['mutation_type']].append(row)

    # Write summary CSV
    with open(summary_csv, 'w') as f:
        f.write('mutation_type,total_tests,response_count,auth_success,auth_failed,conn_error,timeout,p50_remote_ms,p95_remote_ms,crash_count\n')
        for mut in ['valid', 'onebit', 'multibit', 'random', 'allzero', 'allff', 'truncated', 'extended']:
            items = groups.get(mut, [])
            if not items:
                continue

            total = len(items)
            lats = []
            success = 0
            failed = 0
            conn_err = 0
            timeout = 0
            crash = 0

            for item in items:
                lt = item.get('remote_latency_ms', 'NA')
                if lt != 'NA':
                    lats.append(float(lt))

                ar = item.get('auth_result', '')
                if ar == 'success':
                    success += 1
                elif ar == 'auth_failed':
                    failed += 1
                elif ar in ('connection_error',):
                    conn_err += 1
                elif ar == 'timeout':
                    timeout += 1

                if 'sshd_crashed' in item.get('error_info', ''):
                    crash += 1

            lats.sort()
            p50 = lats[int(len(lats) * 0.50)] if lats else -1
            p95 = lats[min(int(len(lats) * 0.95), len(lats) - 1)] if lats else -1

            f.write(f'{mut},{total},{total - conn_err - timeout},{success},{failed},{conn_err},{timeout},{p50:.2f},{p95:.2f},{crash}\n')

    # Generate markdown
    lines = []
    lines.append('# Experiment 3, Table 1: Protocol-Level Observable Behavior')
    lines.append('')
    lines.append(
        '| Ciphertext Class | Trials | Client Response | Response Type | '
        'Response Len (B) | Auth Outcome | p50 Challenge-to-Response (ms) | '
        'p95 Challenge-to-Response (ms) | Crashes |'
    )
    lines.append('|:---|---:|---:|---:|---:|---:|---:|---:|---:|')

    for mut in ['valid', 'onebit', 'multibit', 'random', 'allzero', 'allff', 'truncated', 'extended']:
        items = groups.get(mut, [])
        if not items:
            continue

        total = len(items)
        lats = []
        success = 0
        failed = 0
        conn_err = 0
        timeout = 0
        crash = 0
        resp_types = set()
        resp_lengths = []

        for item in items:
            lt = item.get('remote_latency_ms', 'NA')
            if lt != 'NA':
                lats.append(float(lt))
            ar = item.get('auth_result', '')
            if ar == 'success': success += 1
            elif ar == 'auth_failed': failed += 1
            elif ar in ('connection_error',): conn_err += 1
            elif ar == 'timeout': timeout += 1
            if 'sshd_crashed' in item.get('error_info', ''): crash += 1

                        # Collect response type and length (if available in raw CSV)
            rt = item.get('response_type', '')
            if rt:
                resp_types.add(rt)
            rl = item.get('response_length', '')
            if rl and rl not in ('NA', ''):
                try:
                    resp_lengths.append(int(rl))
                except ValueError:
                    pass

        lats.sort()
        p50 = f'{lats[int(len(lats)*0.50)]:.1f}' if lats else '—'
        p95 = f'{lats[min(int(len(lats)*0.95), len(lats)-1)]:.1f}' if lats else '—'
        responded = success + failed

                # Whether client returned a response
        has_response = 'YES' if responded > 0 else 'NO'

                # Response type: deduplicated summary
        resp_type_str = ', '.join(sorted(resp_types)) if resp_types else '—'

                # Response length: median (should be consistent within class)
        if resp_lengths:
            resp_lengths.sort()
            resp_len_str = str(resp_lengths[len(resp_lengths)//2])
        else:
            resp_len_str = '—'

                # Auth outcome: combined single column
        auth_parts = []
        if success > 0:
            auth_parts.append(f'{success} success')
        if failed > 0:
            auth_parts.append(f'{failed} auth failed')
        if conn_err > 0:
            auth_parts.append(f'{conn_err} conn error')
        if timeout > 0:
            auth_parts.append(f'{timeout} timeout')
        auth_result = ', '.join(auth_parts) if auth_parts else '—'

        lines.append(
            f'| {mut} | {total} | {has_response} | {resp_type_str} | {resp_len_str} | '
            f'{auth_result} | {p50} | {p95} | {crash} |'
        )

    lines.append('')

    if output_md:
        with open(output_md, 'w') as f:
            f.write('\n'.join(lines))
    else:
        print('\n'.join(lines))


def analyze_local(txt_path: str, output_md: str = None):
    """Parse local decaps output."""
    if not os.path.exists(txt_path):
        print(f"[ERR] file not found: {txt_path}")
        return

    with open(txt_path, 'r') as f:
        content = f.read()

        # Find table section
    lines_out = ['# Experiment 3, Table 2: Local Decapsulation Timing', '']
    in_table = False
    for line in content.split('\n'):
        if line.startswith('| Ciphertext'):
            in_table = True
        if in_table:
            lines_out.append(line)
            if line.startswith('|') and not line.startswith('| Ciphertext') and not line.startswith('|:---'):
                pass  # data row
        if in_table and not line.startswith('|') and line.strip() == '':
            in_table = False

    output = '\n'.join(lines_out)
    if output_md:
        with open(output_md, 'w') as f:
            f.write(output)
    else:
        print(output)


def main():
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  analyze_test3.py protocol <raw_csv> <summary_csv> [output_md]", file=sys.stderr)
        print("  analyze_test3.py local <output_txt> [output_md]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'protocol':
        if len(sys.argv) < 4:
            print("[ERR] need raw_csv summary_csv", file=sys.stderr)
            sys.exit(1)
        analyze_protocol(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)

    elif mode == 'local':
        if len(sys.argv) < 3:
            print("[ERR] need output_txt", file=sys.stderr)
            sys.exit(1)
        analyze_local(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)

    else:
        print(f"[ERR] unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
