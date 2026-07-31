#!/usr/bin/env python3
# analyze_test2.py — Exp 2 result analysis
#
# Compute medians from summary.csv, fit M(P)=α+βP, generate testInfo.md §2.1 table.
#
# Usage:
#   python3 analyze_test2.py <summary_csv> [output_md]

import sys
import csv
import os
from collections import defaultdict
from statistics import median
from typing import Dict, List, Optional, Tuple

def load_summary(csv_path: str) -> List[dict]:
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def aggregate(rows: List[dict]) -> Dict[int, Dict[str, dict]]:
    """Group by P and mode, compute medians."""
    groups = defaultdict(lambda: defaultdict(list))

    for row in rows:
        p = int(row['target_concurrency'])
        mode = row['mode']
        groups[p][mode].append(row)

    result = {}
    for p in sorted(groups.keys()):
        result[p] = {}
        for mode in ['kem', 'baseline']:
            items = groups[p].get(mode, [])
            if not items:
                continue

            mems = []
            pendings = []
            residuals = []
            pending_finals = []
            cleaned_ups = []
            for item in items:
                mb = item.get('peak_memory_mb', 'NA')
                pe = item.get('pending_estimate', 'NA')
                rm = item.get('residual_memory_mb', 'NA')
                pf = item.get('pending_final', 'NA')
                cl = item.get('cleaned_up', 'NA')
                if mb != 'NA':
                    mems.append(float(mb))
                if pe != 'NA' and pe.isdigit():
                    pendings.append(int(pe))
                if rm != 'NA':
                    residuals.append(float(rm))
                if pf != 'NA' and pf.lstrip('-').isdigit():
                    pending_finals.append(int(pf))
                if cl != 'NA':
                    cleaned_ups.append(cl)

            result[p][mode] = {
                'peak_mem': median(mems) if mems else None,
                'pending_peak': max(pendings) if pendings else 0,
                'residual_mem': median(residuals) if residuals else None,
                'pending_final': pending_finals[-1] if pending_finals else None,
                'cleaned_up': cleaned_ups[-1] if cleaned_ups else '—',
            }

    return result

def linear_fit(xs: List[float], ys: List[float]) -> Optional[Tuple[float, float]]:
    """Simple linear regression y = α + βx. Returns (α, β)."""
    if len(xs) < 2:
        return None
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom == 0:
        return None
    beta = (n * sxy - sx * sy) / denom
    alpha = (sy - beta * sx) / n
    return alpha, beta

def fmt(val, template='.2f', na='—'):
    if val is None:
        return na
    return f'{val:{template}}'

def generate_markdown(agg: dict, explicit_state_kib: float = None) -> str:
    """Generate Markdown table in testInfo.md §2.1 format.

    Args:
        agg: aggregated data
        explicit_state_kib: explicit state/challenge size (KiB), to be filled in
                            from static code analysis. If None, shows "—".
    """
    lines = []
    lines.append('# Exp 2: Pending KEM Challenge State and Memory Growth — Results Summary')
    lines.append('')
    lines.append('## 2.1 Results Summary Table')
    lines.append('')
    lines.append(
        '| Target Concurrent Connections P | KEMUAuth Peak Memory (MB) | Baseline SSH/ML-DSA Peak Memory (MB) | '
        'Observed Memory Delta (MB) | Measured Peak Pending P_max | Explicit State/Challenge (KiB) | '
        'Theoretical State Total (MB) | Timely Cleanup | Residual Memory After Disconnect (MB) |'
    )
    lines.append('|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|')

    # Data for linear fit
    ps_fit = []
    mems_fit = []

    # Explicit state value (KiB → MB conversion)
    s_explicit_kib = explicit_state_kib
    s_explicit_mb = (s_explicit_kib / 1024.0) if s_explicit_kib is not None else None

    for p in sorted(agg.keys()):
        kem = agg[p].get('kem', {})
        baseline = agg[p].get('baseline', {})

        kem_mem = fmt(kem.get('peak_mem'))
        base_mem = fmt(baseline.get('peak_mem'))

        mem_diff = '—'
        if kem.get('peak_mem') is not None and baseline.get('peak_mem') is not None:
            diff = kem['peak_mem'] - baseline['peak_mem']
            mem_diff = f'{diff:+.2f}'
            if p > 0:
                ps_fit.append(float(p))
                mems_fit.append(float(kem['peak_mem']))

        pending_peak = kem.get('pending_peak', 0)

        # Explicit state/Challenge (KiB)
        explicit_str = f'{s_explicit_kib:.1f}' if s_explicit_kib is not None else '—'

        # Theoretical state total = P_max × S_explicit (MB)
        theory_str = '—'
        if s_explicit_mb is not None and pending_peak > 0:
            theory_mb = pending_peak * s_explicit_mb
            theory_str = f'{theory_mb:.2f}'

        # Timely cleanup: judge by pending final count and residual
        cleaned = kem.get('cleaned_up', '—')
        if cleaned == '—' or cleaned is None:
            # Judge by pending_estimate returning to 0 + residual memory
            pending_final = kem.get('pending_final', None)
            residual_val = kem.get('residual_mem')
            if pending_final is not None:
                cleaned = 'YES' if pending_final == 0 else 'NO'
            elif residual_val is not None and residual_val < 1.0:
                cleaned = 'YES'
            else:
                cleaned = '—'

        residual = fmt(kem.get('residual_mem'))

        lines.append(
            f'| {p} | {kem_mem} | {base_mem} | {mem_diff} | {pending_peak} | '
            f'{explicit_str} | {theory_str} | {cleaned} | {residual} |'
        )

    lines.append('')

    # Linear fit
    if len(ps_fit) >= 2:
        fit = linear_fit(ps_fit, mems_fit)
        if fit:
            alpha, beta = fit
            lines.append('## Memory Growth Fit')
            lines.append('')
            lines.append(f'$$M(P) = {alpha:.2f} + {beta:.4f} \\cdot P$$')
            lines.append('')
            lines.append(f'- α (base memory): {alpha:.2f} MB')
            lines.append(f'- β (per pending connection increment): {beta:.4f} MB/conn = {beta*1024:.2f} KiB/conn')
            lines.append('')
            lines.append('| P | Measured KEMUAuth Memory (MB) | Fitted (MB) | Residual (MB) |')
            lines.append('|:---:|:---:|:---:|:---:|')
            for p, m in zip(ps_fit, mems_fit):
                fitted = alpha + beta * p
                residual = m - fitted
                lines.append(f'| {int(p)} | {m:.2f} | {fitted:.2f} | {residual:+.2f} |')
            lines.append('')

    # Explicit state calculation
    lines.append('## Explicit State Estimate')
    lines.append('')
    lines.append('Fill in after computing `sizeof(pending_state) + sum(len(dynamic_buffer))` from code:')
    lines.append('')
    lines.append('| Field | Size (bytes) |')
    lines.append('|:---|:---:|')
    lines.append('| shared_secret | — |')
    lines.append('| ciphertext | — |')
    lines.append('| alg_name | — |')
    lines.append('| session_id / transcript | — |')
    lines.append('| timestamp / flags | — |')
    lines.append('| **Total (S_explicit)** | **—** |')
    lines.append('')

    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <summary_csv> [output_md] [--explicit-state-kib N]", file=sys.stderr)
        print(f"  --explicit-state-kib  explicit state size (KiB), from static code analysis", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = None
    explicit_state_kib = None

    for arg in sys.argv[2:]:
        if arg == '--explicit-state-kib':
            continue
        if arg.startswith('--explicit-state-kib='):
            try:
                explicit_state_kib = float(arg.split('=', 1)[1])
            except ValueError:
                print(f"[WARN] invalid --explicit-state-kib value: {arg}", file=sys.stderr)
        elif not arg.startswith('--'):
            output_path = arg

    # Also support environment variable
    if explicit_state_kib is None:
        env_val = os.environ.get('EXPLICIT_STATE_KIB', '')
        if env_val:
            try:
                explicit_state_kib = float(env_val)
            except ValueError:
                pass

    if not os.path.exists(csv_path):
        print(f"[ERR] file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    rows = load_summary(csv_path)
    agg = aggregate(rows)
    md = generate_markdown(agg, explicit_state_kib=explicit_state_kib)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(md)
        print(f"[INFO] report -> {output_path}")
    else:
        print(md)

if __name__ == '__main__':
    main()
