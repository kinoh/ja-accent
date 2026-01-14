# Katakana normalization for pronunciation

## Context
- The user reported `/accent` returned `イ'イヨネっ` for "いいよねっ", leaving a trailing hiragana `っ`.
- UniDic provides multiple reading fields and some entries expose hiragana or `*` in the current pronunciation slot.

## Decision
- Keep the primary pronunciation field unchanged and fill missing pronunciation only for the small tsu `っ`.

## Rationale
- Mora splitting and accent formatting assume katakana, so normalization keeps outputs consistent.
- Using dictionary-provided readings preserves intended pronunciation when available.

## Notes
- No interface changes.
