# test2-C (Generated)

Run config: rounds=1, warmup=0, iterations=3, RTT=37ms, initcwnd=10

| Case | Client Algorithm | Server Algorithm | Mean (ms) | 50th (ms) | 95th (ms) |
|---|---|---|---:|---:|---:|
| classic | ed25519 | ed25519 | 519.288 | 518.761 | 520.622 |
| hybrid_md65_ed25519 | md65 + ed25519 | md65 + ed25519 | 522.878 | 522.880 | 523.380 |
| hybrid_sd192f_ed25519 | sd192f + ed25519 | sd192f + ed25519 | 578.326 | 578.485 | 579.164 |
| migration_kem768_server_md65_ed25519 | mk768 + ed25519 | md65 + ed25519 | 521.082 | 521.333 | 521.515 |
| migration_kem768_server_sd192f_ed25519 | mk768 + ed25519 | sd192f + ed25519 | 522.537 | 522.543 | 522.967 |
| chain_ed25519_to_md65 | ed25519 -> md65 | md65 + ed25519 | 605.141 | 605.291 | 605.466 |
| chain_ed25519_to_mk768 | ed25519 -> mk768 | md65 + ed25519 | 604.991 | 604.964 | 605.603 |
| pure_pq_userauth_path | mk768 | md65 | 516.300 | 516.450 | 516.659 |
