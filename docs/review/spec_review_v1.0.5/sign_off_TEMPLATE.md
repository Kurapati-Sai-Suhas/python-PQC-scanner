# Specification review sign-off (protocol v1.0.5) — TEMPLATE

Copy this file before filling it in. Leave a field as `TO FILL` rather than guessing.

This review is "ChatGPT review with owner sign-off" (protocol v1.0.5, Sec. 3). It is an AI review plus the owner's decisions. It is not an independent human review and is not reported as one.

## 1. Session

- Identity record used: `docs/benchmark/ai_review_identity.json`, SHA-256: TO FILL
- Session date and time (UTC): TO FILL
- Interface and model, as shown in the session: TO FILL
- App version, if shown (guide v1.1 Sec. 6; otherwise write "not shown"): TO FILL
- Isolation settings confirmed before pasting (yes/no for each): Temporary Chat TO FILL; custom instructions off TO FILL; memory and chat history off TO FILL; Projects off TO FILL; connectors off TO FILL; file library off TO FILL; browsing off TO FILL
- Number of sessions started (including any restarted): TO FILL. Reason for any restart: TO FILL

## 2. Packet

- `python scripts/spec_review_packet.py --check` exit code on the day: TO FILL
- `packet/manifest.json` SHA-256: TO FILL
- Git commit the packet was taken from: TO FILL
- All 8 parts acknowledged as `RECEIVED PART i OF 8` (yes/no): TO FILL

## 3. Reply

- Where the verbatim reply and conversation export are stored: TO FILL
- SHA-256 of the saved reply: TO FILL
- Number of findings: critical TO FILL, major TO FILL, minor TO FILL

## 4. Decisions

- Decision sheet (copy of `owner_decisions_TEMPLATE.csv`): TO FILL
- Accepted TO FILL, rejected TO FILL, deferred TO FILL
- Findings that require a protocol amendment, and the amendment decision for each: TO FILL
- Known points decided (pilot figure, W6, D10): TO FILL

## 5. Sign-off

I have read every finding and recorded a decision and reason for each. No threshold, sample size, sampling order, confirmatory family or baseline was changed without a separate recorded decision.

- Owner: TO FILL
- Date (UTC): TO FILL
