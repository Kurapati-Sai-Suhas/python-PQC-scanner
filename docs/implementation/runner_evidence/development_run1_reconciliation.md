# Batch runner: first real run, reconciled with the pilot (development check)

Run directory: `runs/development/run1`. Not a result: the pilot repositories are development repositories.

## Run records

| Method | Repository | Status | Exit | Timed out | Seconds | File status |
|---|---|---|---|---|---|---|
| pqcheck | jpadilla__pyjwt | ok | 1 | False | 5.735 | {'processed': 26} |
| pqc-audit | jpadilla__pyjwt | ok | 0 | False | 1.25 | {'processed': 26} |
| PostQuant | jpadilla__pyjwt | ok | 1 | False | 0.969 | {'processed': 26} |
| qsafe | jpadilla__pyjwt | ok | 0 | False | 0.671 | {'processed': 26} |
| QSA-regex | jpadilla__pyjwt | ok | 0 | False | 78.765 | {'processed': 26} |
| pqblocks-scan | jpadilla__pyjwt | ok | 0 | False | 0.657 | {'processed': 26} |
| pqscan:full | jpadilla__pyjwt | ok | 0 | False | 7.235 | {'processed': 26} |
| pqscan:method+args+recv | jpadilla__pyjwt | ok | 0 | False | 5.015 | {'processed': 26} |
| pqscan:method+args | jpadilla__pyjwt | ok | 0 | False | 5.063 | {'processed': 26} |
| pqscan:method-only | jpadilla__pyjwt | ok | 0 | False | 5.422 | {'processed': 26} |
| pqcheck | lepture__authlib | ok | 1 | False | 18.719 | {'processed': 389} |
| pqc-audit | lepture__authlib | ok | 0 | False | 1.062 | {'processed': 389} |
| PostQuant | lepture__authlib | ok | 1 | False | 44.188 | {'processed': 389} |
| qsafe | lepture__authlib | ok | 0 | False | 2.703 | {'processed': 389} |
| QSA-regex | lepture__authlib | ok | 0 | False | 4.641 | {'processed': 389} |
| pqblocks-scan | lepture__authlib | ok | 0 | False | 0.844 | {'processed': 389} |
| pqscan:full | lepture__authlib | ok | 0 | False | 12.375 | {'processed': 389} |
| pqscan:method+args+recv | lepture__authlib | ok | 0 | False | 12.421 | {'processed': 389} |
| pqscan:method+args | lepture__authlib | ok | 0 | False | 12.422 | {'processed': 389} |
| pqscan:method-only | lepture__authlib | ok | 0 | False | 12.641 | {'processed': 389} |
| pqcheck | mpdavis__python-jose | ok | 1 | False | 1.734 | {'processed': 38} |
| pqc-audit | mpdavis__python-jose | ok | 0 | False | 0.344 | {'processed': 38} |
| PostQuant | mpdavis__python-jose | ok | 1 | False | 1.172 | {'processed': 38} |
| qsafe | mpdavis__python-jose | ok | 0 | False | 0.5 | {'processed': 38} |
| QSA-regex | mpdavis__python-jose | ok | 0 | False | 2.5 | {'processed': 38} |
| pqblocks-scan | mpdavis__python-jose | ok | 0 | False | 0.203 | {'processed': 38} |
| pqscan:full | mpdavis__python-jose | ok | 0 | False | 4.453 | {'processed': 38} |
| pqscan:method+args+recv | mpdavis__python-jose | ok | 0 | False | 4.422 | {'processed': 38} |
| pqscan:method+args | mpdavis__python-jose | ok | 0 | False | 4.468 | {'processed': 38} |
| pqscan:method-only | mpdavis__python-jose | ok | 0 | False | 4.438 | {'processed': 38} |
| pqcheck | paramiko__paramiko | ok | 1 | False | 3.641 | {'processed': 70} |
| pqc-audit | paramiko__paramiko | ok | 0 | False | 0.75 | {'processed': 70} |
| PostQuant | paramiko__paramiko | ok | 1 | False | 2.25 | {'processed': 70} |
| qsafe | paramiko__paramiko | ok | 0 | False | 1.172 | {'processed': 70} |
| QSA-regex | paramiko__paramiko | ok | 0 | False | 3.329 | {'processed': 70} |
| pqblocks-scan | paramiko__paramiko | ok | 0 | False | 0.422 | {'processed': 70} |
| pqscan:full | paramiko__paramiko | ok | 0 | False | 4.656 | {'processed': 70} |
| pqscan:method+args+recv | paramiko__paramiko | ok | 0 | False | 4.703 | {'processed': 70} |
| pqscan:method+args | paramiko__paramiko | ok | 0 | False | 4.797 | {'processed': 70} |
| pqscan:method-only | paramiko__paramiko | ok | 0 | False | 4.781 | {'processed': 70} |

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
