# test1 (Unified Figure-3 dataset)

- Goal: generate the unified Figure-3 dataset (client-authentication algorithm
  comparison, RTT=67ms, initcwnd=10 MSS, server host-key Ed25519) covering 13
  algorithms in one campaign: Ed25519, ML-DSA-44/65/87, Falcon-512/1024,
  SLH-DSA-SHA2-128f/192f/256f, ML-KEM-512/768/1024, and Password (yescrypt).
- Unified runner: testScripts/fig3_rerun/run (interleaved round-robin polling to
  amortize environment drift)
- Data source: testScripts/fig3_rerun/run -> results in testScripts/fig3_rerun/results/
- Pre-computed results: [reference_data.md](reference_data.md) (13-algorithm unified
  table, 2000 samples per algorithm, 0 failures)
- Output files (in testScripts/fig3_rerun/results/):
	- raw_runs.csv
	- summary.csv
	- readable.md
	- metadata.txt
- Run the unified campaign:
	- `sudo bash testScripts/fig3_rerun/run`
	- Quick smoke: `sudo env ITERATIONS=5 WARMUP=1 bash testScripts/fig3_rerun/run`
- Run all tests: bash testScripts/run_all

## Notes

- Requires root (test account creation, tc, ip route initcwnd, ethtool).
- This unified runner replaces the earlier separate test1 (10 algorithms),
  `supp_falcon/`, and `supp_password/` extension tables.
