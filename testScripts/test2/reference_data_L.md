# test2-L (Generated)

Run config: rounds=1, warmup=0, iterations=3, RTT=163ms, initcwnd=10

| Case | Client Algorithm | Server Algorithm | Mean (ms) | 50th (ms) | 95th (ms) |
|---|---|---|---:|---:|---:|
| classic | ed25519 | ed25519 | 1907.564 | 1907.760 | 1908.260 |
| hybrid_md65_ed25519 | md65 + ed25519 | md65 + ed25519 | 1908.835 | 1908.680 | 1909.326 |
| hybrid_sd192f_ed25519 | sd192f + ed25519 | sd192f + ed25519 | 2091.468 | 2091.447 | 2091.630 |
| migration_kem768_server_md65_ed25519 | mk768 + ed25519 | md65 + ed25519 | 1905.874 | 1905.866 | 1906.453 |
| migration_kem768_server_sd192f_ed25519 | mk768 + ed25519 | sd192f + ed25519 | 1907.606 | 1907.442 | 1908.052 |
| chain_ed25519_to_md65 | ed25519 -> md65 | md65 + ed25519 | 2241.803 | 2241.567 | 2242.294 |
| chain_ed25519_to_mk768 | ed25519 -> mk768 | md65 + ed25519 | 2237.995 | 2238.451 | 2238.507 |
| pure_pq_userauth_path | mk768 | md65 | 1903.273 | 1903.609 | 1903.655 |
