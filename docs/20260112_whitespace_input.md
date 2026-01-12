# Whitespace handling in /accent input

## Context
- The /accent endpoint crashed with `not enough values to unpack (expected 13, got 12)` when the input text contained spaces.
- The user confirmed the request uses the `text` field (not `message`).

## Decision
- Remove all Unicode whitespace except newline after pyopenjtalk segmentation so MeCab never sees whitespace-only tokens.
- Keep behavior aligned with prior logic that already removed ASCII spaces, but broaden it to fullwidth and other whitespace.

## Rationale
- Whitespace-only tokens collapse fields when `dataline.split()` is used in `mkdata_accent_text`, causing the unpack error.
- Preserving newlines keeps phrase boundary behavior unchanged.

## Notes
- No library changes.
- No interface changes.
