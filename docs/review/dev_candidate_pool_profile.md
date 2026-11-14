# Candidate-pool profile, development repositories only (planning aid for D2)

Unit: distinct (file, line) candidates. `regex_only` = candidates no evaluated tool reported; `tools_only` = reported by a tool but not matched by the regex; `lib_*` = crypto library imported by the file. No correctness figure is computed.

| Repository | union | regex | tools | both | regex_only | tools_only | test_path | lib_pyca | lib_pycryptodome | lib_both | lib_none |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jpadilla__pyjwt | 550 | 197 | 434 | 81 | 116 | 353 | 380 | 460 | 0 | 0 | 90 |
| lepture__authlib | 1139 | 243 | 1053 | 157 | 86 | 896 | 760 | 570 | 1 | 0 | 568 |
| mpdavis__python-jose | 367 | 35 | 362 | 30 | 5 | 332 | 191 | 101 | 0 | 33 | 233 |
| paramiko__paramiko | 746 | 116 | 737 | 107 | 9 | 630 | 422 | 505 | 0 | 0 | 241 |
| TOTAL | 2802 | 591 | 2586 | 375 | 216 | 2211 | 1753 | 1636 | 1 | 33 | 1132 |

Pilot sites (31; paramiko and python-jose) inside each candidate source:

- regex: 30 of 31
- tool union: 31 of 31
- full union: 31 of 31
