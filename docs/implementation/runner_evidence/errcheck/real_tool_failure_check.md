# Real-tool failure check on the four-file fixture

| Tool | Run status | Exit | File status (runner) | EXECUTION_FAILURE sites (judge) | Expected (measured profile) | MISSED | Match |
|---|---|---|---|---|---|---|---|
| pqcheck | ok | 1 | {'processed': 2, 'skipped-by-profile': 2} | ['nullbyte.py', 'syntax_error.py'] | ['nullbyte.py', 'syntax_error.py'] | [] | yes |
| pqc-audit | ok | 0 | {'processed': 2, 'skipped-by-profile': 2} | ['nullbyte.py', 'syntax_error.py'] | ['nullbyte.py', 'syntax_error.py'] | [] | yes |
| PostQuant | ok | 1 | {'processed': 4} | [] | [] | [] | yes |
| qsafe | ok | 0 | {'processed': 4} | [] | [] | [] | yes |
| QSA-regex | ok | 0 | {'processed': 3, 'skipped-by-profile': 1} | ['nullbyte.py'] | ['nullbyte.py'] | [] | yes |
| pqblocks-scan | failed | 2 | {'run-failed': 4} | ['good.py', 'latin1.py', 'nullbyte.py', 'syntax_error.py'] | ['good.py', 'latin1.py', 'nullbyte.py', 'syntax_error.py'] | [] | yes |
| pqscan:full | ok | 0 | {'logged-failure': 2, 'processed': 2} | (own execution_failures list) | syntax-error, null-byte | - | - |
