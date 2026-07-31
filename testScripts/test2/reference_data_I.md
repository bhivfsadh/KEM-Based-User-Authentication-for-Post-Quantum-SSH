# test2-I (Generated)

Run config: rounds=1, warmup=0, iterations=3, RTT=67ms, initcwnd=10

| Case | Client Algorithm | Server Algorithm | Mean (ms) | 50th (ms) | 95th (ms) |
|---|---|---|---:|---:|---:|
| classic | ed25519 | ed25519 | 850.768 | 850.726 | 851.093 |
| hybrid_md65_ed25519 | md65 + ed25519 | md65 + ed25519 | 849.725 | 849.660 | 850.446 |
| hybrid_sd192f_ed25519 | sd192f + ed25519 | sd192f + ed25519 | 938.693 | 938.407 | 939.436 |
| migration_kem768_server_md65_ed25519 | mk768 + ed25519 | md65 + ed25519 | 851.809 | 852.126 | 852.619 |
| migration_kem768_server_sd192f_ed25519 | mk768 + ed25519 | sd192f + ed25519 | 848.851 | 848.658 | 849.736 |
| chain_ed25519_to_md65 | ed25519 -> md65 | md65 + ed25519 | 996.510 | 996.792 | 996.954 |
| chain_ed25519_to_mk768 | ed25519 -> mk768 | md65 + ed25519 | 991.254 | 991.314 | 991.409 |
| pure_pq_userauth_path | mk768 | md65 | 848.181 | 847.728 | 849.392 |
