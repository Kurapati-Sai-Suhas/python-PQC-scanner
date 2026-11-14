# Batch runner: first real run, reconciled with the pilot (development check)

Run directory: `runs/development/run2`. Not a result: the pilot repositories are development repositories.

## Run records

| Method | Repository | Status | Exit | Timed out | Seconds | File status |
|---|---|---|---|---|---|---|
| pqcheck | jpadilla__pyjwt | ok | 1 | False | 0.954 | {'processed': 26} |
| pqc-audit | jpadilla__pyjwt | ok | 0 | False | 0.312 | {'processed': 26} |
| PostQuant | jpadilla__pyjwt | ok | 1 | False | 0.953 | {'processed': 26} |
| qsafe | jpadilla__pyjwt | ok | 0 | False | 0.531 | {'processed': 26} |
| QSA-regex | jpadilla__pyjwt | ok | 0 | False | 2.688 | {'processed': 26} |
| pqblocks-scan | jpadilla__pyjwt | ok | 0 | False | 0.265 | {'processed': 26} |
| pqscan:full | jpadilla__pyjwt | ok | 0 | False | 4.516 | {'processed': 26} |
| pqscan:method+args+recv | jpadilla__pyjwt | ok | 0 | False | 4.563 | {'processed': 26} |
| pqscan:method+args | jpadilla__pyjwt | ok | 0 | False | 4.391 | {'processed': 26} |
| pqscan:method-only | jpadilla__pyjwt | ok | 0 | False | 4.422 | {'processed': 26} |
| pqcheck | lepture__authlib | ok | 1 | False | 1.875 | {'processed': 389} |
| pqc-audit | lepture__authlib | ok | 0 | False | 0.719 | {'processed': 389} |
| PostQuant | lepture__authlib | ok | 1 | False | 10.938 | {'processed': 389} |
| qsafe | lepture__authlib | ok | 0 | False | 2.843 | {'processed': 389} |
| QSA-regex | lepture__authlib | ok | 0 | False | 4.765 | {'processed': 389} |
| pqblocks-scan | lepture__authlib | ok | 0 | False | 0.86 | {'processed': 389} |
| pqscan:full | lepture__authlib | ok | 0 | False | 12.516 | {'processed': 389} |
| pqscan:method+args+recv | lepture__authlib | ok | 0 | False | 12.578 | {'processed': 389} |
| pqscan:method+args | lepture__authlib | ok | 0 | False | 12.656 | {'processed': 389} |
| pqscan:method-only | lepture__authlib | ok | 0 | False | 12.563 | {'processed': 389} |
| pqcheck | mpdavis__python-jose | ok | 1 | False | 0.891 | {'processed': 38} |
| pqc-audit | mpdavis__python-jose | ok | 0 | False | 0.313 | {'processed': 38} |
| PostQuant | mpdavis__python-jose | ok | 1 | False | 1.156 | {'processed': 38} |
| qsafe | mpdavis__python-jose | ok | 0 | False | 0.407 | {'processed': 38} |
| QSA-regex | mpdavis__python-jose | ok | 0 | False | 2.547 | {'processed': 38} |
| pqblocks-scan | mpdavis__python-jose | ok | 0 | False | 0.218 | {'processed': 38} |
| pqscan:full | mpdavis__python-jose | ok | 0 | False | 4.516 | {'processed': 38} |
| pqscan:method+args+recv | mpdavis__python-jose | ok | 0 | False | 4.563 | {'processed': 38} |
| pqscan:method+args | mpdavis__python-jose | ok | 0 | False | 4.468 | {'processed': 38} |
| pqscan:method-only | mpdavis__python-jose | ok | 0 | False | 4.438 | {'processed': 38} |
| pqcheck | paramiko__paramiko | ok | 1 | False | 1.188 | {'processed': 70} |
| pqc-audit | paramiko__paramiko | ok | 0 | False | 0.422 | {'processed': 70} |
| PostQuant | paramiko__paramiko | ok | 1 | False | 2.266 | {'processed': 70} |
| qsafe | paramiko__paramiko | ok | 0 | False | 1.125 | {'processed': 70} |
| QSA-regex | paramiko__paramiko | ok | 0 | False | 3.422 | {'processed': 70} |
| pqblocks-scan | paramiko__paramiko | ok | 0 | False | 0.422 | {'processed': 70} |
| pqscan:full | paramiko__paramiko | ok | 0 | False | 4.765 | {'processed': 70} |
| pqscan:method+args+recv | paramiko__paramiko | ok | 0 | False | 4.781 | {'processed': 70} |
| pqscan:method+args | paramiko__paramiko | ok | 0 | False | 4.781 | {'processed': 70} |
| pqscan:method-only | paramiko__paramiko | ok | 0 | False | 4.703 | {'processed': 70} |

Not run: CBOMkit (sonar-cryptography), Mehl ESEM 2026 scanner.

## Judgments on the 31 pilot sites vs. the published pilot table

| Tool | Sites | Same as published | Different | Execution failures |
|---|---|---|---|---|
| pqcheck | 31 | 31 | 0 | 0 |
| pqc-audit | 31 | 31 | 0 | 0 |
| PostQuant | 31 | 31 | 0 | 0 |
| qsafe | 31 | 31 | 0 | 0 |
| QSA-regex | 31 | 31 | 0 | 0 |
| pqblocks-scan (not in the published pilot table) | 31 | n/a | n/a | 0 |
