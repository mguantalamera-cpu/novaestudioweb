# Security Model

## Scope
SecurePatch scans local project files selected by the user. It does not execute project code.

## Threats
- Untrusted files (large, binary, or malicious payloads)
- Path traversal or symlink tricks
- UI freezing on large projects

## Mitigations
- File size limits and binary detection
- Skip symlinks and excluded directories
- Background worker threads
- No network scanning or exploit generation

## Privacy
- Offline-first, no outbound transmission of source code by default.
- Any remote LLM mode must be explicitly enabled by the user.
