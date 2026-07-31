#!/usr/bin/env python3
# result_aggregator.py — generic result aggregation tool
#
# Features:
#   1. Compute median per (group_key, subgroup_key) across metrics
#   2. Merge multiple CSV files
#   3. Generate Markdown tables
#
# Usage:
#   python3 result_aggregator.py merge <output.csv> <file1.csv> <file2.csv> ...
#   python3 result_aggregator.py aggregate <input.csv> --group-by <col> --metrics <col1,col2,...>
#   python3 result_aggregator.py table <input.csv> --group-by <col> --subgroup <col> --cols <col1,col2,...>

import sys
import csv
import os
from collections import defaultdict, OrderedDict
from statistics import median
from typing import Optional


# ---- Utility functions ----

def load_csv(csv_path: str) -> list:
    """Load CSV file, return list of dicts."""
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_csv(csv_path: str, rows: list, fieldnames: list):
    """Save CSV file."""
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(val, template='.2f', na='—'):
    if val is None:
        return na
    return f'{val:{template}}'


# ---- merge: merge multiple CSVs ----

def cmd_merge(output: str, inputs: list):
    """Merge multiple CSV files, keeping intersection of columns."""
    all_rows = []
    common_cols = None

    for csv_file in inputs:
        if not os.path.exists(csv_file):
            print(f"[WARN] skipping missing file: {csv_file}")
            continue
        rows = load_csv(csv_file)
        if not rows:
            continue
        cols = set(rows[0].keys())
        if common_cols is None:
            common_cols = cols
        else:
            common_cols = common_cols & cols
        all_rows.extend(rows)

    if common_cols is None:
        print("[ERR] no data found")
        sys.exit(1)

    # Filter to common columns
    filtered = [{k: row[k] for k in common_cols} for row in all_rows]
    save_csv(output, filtered, list(common_cols))
    print(f"[INFO] merged {len(inputs)} files → {output} ({len(filtered)} rows, {len(common_cols)} cols)")


# ---- aggregate: aggregate by group ----

def cmd_aggregate(input_csv: str, group_by: str, metrics: Optional[str] = None):
    """Aggregate by group_by column, compute median for each metric column."""
    rows = load_csv(input_csv)
    metric_cols = metrics.split(',') if metrics else []

    groups = defaultdict(list)
    for row in rows:
        key = row.get(group_by, '__unknown__')
        groups[key].append(row)

    result = []
    for key in sorted(groups.keys()):
        group_rows = groups[key]
        agg_row = {group_by: key, 'count': len(group_rows)}

        cols_to_agg = metric_cols if metric_cols else [
            c for c in group_rows[0].keys()
            if c != group_by and group_rows[0][c].replace('.', '', 1).replace('-', '', 1).isdigit()
        ]

        for col in cols_to_agg:
            if col in agg_row:
                continue
            vals = []
            for row in group_rows:
                val = row.get(col, '')
                try:
                    vals.append(float(val))
                except (ValueError, TypeError):
                    pass
            if vals:
                agg_row[f'{col}_median'] = round(median(vals), 4)
                agg_row[f'{col}_min'] = round(min(vals), 4)
                agg_row[f'{col}_max'] = round(max(vals), 4)

        result.append(agg_row)

    fieldnames = list(result[0].keys()) if result else []
    output = input_csv.replace('.csv', '_aggregated.csv')
    save_csv(output, result, fieldnames)
    print(f"[INFO] aggregated {len(rows)} rows → {len(result)} groups → {output}")


# ---- table: generate Markdown table ----

def cmd_table(input_csv: str, group_by: str, subgroup: Optional[str] = None,
              cols: Optional[str] = None):
    """Generate Markdown table from CSV."""
    rows = load_csv(input_csv)
    col_list = cols.split(',') if cols else list(rows[0].keys())

    # Filter out non-display columns
    display_cols = [c for c in col_list if c not in (group_by, subgroup)]

    if subgroup:
        # 2D table: rows=group_by, cols=subgroup × metrics
        table_data = defaultdict(lambda: defaultdict(dict))
        for row in rows:
            gk = row.get(group_by, '—')
            sk = row.get(subgroup, '—')
            for col in display_cols:
                table_data[gk][f'{sk}_{col}'] = row.get(col, '—')

        # Generate header
        sub_keys = sorted(set(
            row.get(subgroup, '—') for row in rows
        ))
        header = f'| {group_by} | ' + ' | '.join(
            f'{sk} {col}' for sk in sub_keys for col in display_cols
        ) + ' |'

        print(header)
        print('|' + '|'.join([':---:'] * (1 + len(sub_keys) * len(display_cols))) + '|')

        for gk in sorted(table_data.keys()):
            vals = []
            for sk in sub_keys:
                for col in display_cols:
                    vals.append(str(table_data[gk].get(f'{sk}_{col}', '—')))
            print(f'| {gk} | ' + ' | '.join(vals) + ' |')
    else:
        # 1D table
        print(f'| {" | ".join(col_list)} |')
        print('|' + '|'.join([':---:'] * len(col_list)) + '|')
        for row in rows:
            print('| ' + ' | '.join(str(row.get(c, '—')) for c in col_list) + ' |')


# ---- main ----

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 result_aggregator.py merge <output.csv> <file1.csv> ...")
        print("  python3 result_aggregator.py aggregate <input.csv> --group-by <col> [--metrics col1,col2]")
        print("  python3 result_aggregator.py table <input.csv> --group-by <col> [--subgroup <col>] [--cols col1,col2]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'merge':
        if len(sys.argv) < 4:
            print("[ERR] merge requires: <output.csv> <file1.csv> ...")
            sys.exit(1)
        cmd_merge(sys.argv[2], sys.argv[3:])

    elif cmd == 'aggregate':
        args = sys.argv[2:]
        input_csv = args[0]
        group_by = None
        metrics = None
        i = 1
        while i < len(args):
            if args[i] == '--group-by' and i + 1 < len(args):
                group_by = args[i + 1]
                i += 1
            elif args[i] == '--metrics' and i + 1 < len(args):
                metrics = args[i + 1]
                i += 1
            i += 1
        if not group_by:
            print("[ERR] --group-by is required")
            sys.exit(1)
        cmd_aggregate(input_csv, group_by, metrics)

    elif cmd == 'table':
        args = sys.argv[2:]
        input_csv = args[0]
        group_by = None
        subgroup = None
        cols = None
        i = 1
        while i < len(args):
            if args[i] == '--group-by' and i + 1 < len(args):
                group_by = args[i + 1]
                i += 1
            elif args[i] == '--subgroup' and i + 1 < len(args):
                subgroup = args[i + 1]
                i += 1
            elif args[i] == '--cols' and i + 1 < len(args):
                cols = args[i + 1]
                i += 1
            i += 1
        if not group_by:
            print("[ERR] --group-by is required")
            sys.exit(1)
        cmd_table(input_csv, group_by, subgroup, cols)

    else:
        print(f"[ERR] unknown command: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
