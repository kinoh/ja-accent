# Split Sentence Fix

## Problem
Sentence delimiters (！、。、… etc.) were being ignored in the output, causing multiple sentences to be joined with `/` instead of `、`.

Example:
- Input: `そうなの！ いいよね`
- Expected: `ソオナ'ノ、イ'イヨネ`
- Actual (before): `ソオナ'ノ/イ'イヨネ`

## Root Cause
The `convert_long_vowel_mark` function was removing punctuation marks (`。！…〜～ー・`) that "VOICEVOX doesn't accept", but this was too aggressive. The actual issue was that sentence boundary markers detected by pyopenjtalk should be converted to `、` rather than preserved as-is or deleted.

## Solution
Modified `format_accent_text` in `src/format_accent.py` to convert all auxiliary symbols with `boundary_flag == '/'` (sentence boundaries detected by pyopenjtalk) to `、` instead of preserving the original character.

This approach correctly handles:
- Any punctuation mark (。！？…)
- Emoji or other Unicode characters
- Multiple consecutive delimiters

### Changes
In `format_accent_text` (src/format_accent.py:76-168), changed three locations where auxiliary symbols with `boundary_flag == '/'` are output:

1. Line ~116: `separators.append('、')` instead of `separators.append(aux_orth)`
2. Line ~143: Same change
3. Line ~154: List comprehension to convert `boundary == '/'` to `、`

## Additional Fix: Unknown Words (Emoji)

When testing with emoji (`わかった☺覚えとくね`), an error occurred because MeCab returns very few fields for unknown words (only 6 fields instead of 25-31), and they lack pronunciation information.

### Solution
Modified `seikei_from_mecab` in `src/text2accent.py` to treat unknown words as auxiliary symbols:
- If MeCab returns fewer than 25 fields, treat the word as an auxiliary symbol (set `pron = "*"`)
- Use the surface form (emoji, unknown character, etc.) as the orthographic form
- This allows the word to be properly handled by `format_accent_text` as a sentence boundary

### Changes
Added a new condition block before the existing `len(f) == 25` check:
```python
if len(f) < 25:
    # Treat as auxiliary symbol with pron = "*"
```

Also removed the fallback `else` block that was outputting incorrect field counts.

## Test Results
✓ `そうなの！ いいよね` → `ソオナ'ノ、イ'イヨネ`
✓ `こんにちは。世界` → `コンニチワ'、セ'カイ`
✓ `やった…！最高だよ` → `ヤッタ'、サイコオダ'ヨ`
✓ `わかった☺覚えとくね` → `ワカ'ッタ、オボエト'クネ`

## Notes
- VOICEVOX compatible separators are `/` (accent phrase boundary) and `、` (sentence/pause boundary)
- The fix relies on pyopenjtalk's sentence boundary detection, so any character that pyopenjtalk identifies as a sentence boundary will be converted to `、`

## Additional Fix: Preserve ？ for Rising Intonation

`？` (question mark) should be preserved in the output because it indicates rising intonation at the end of a sentence, unlike other punctuation which becomes pause markers.

### Solution
Modified both `format_accent_text` and `normalize_punctuation`:
- In `format_accent_text` (src/format_accent.py): Check if `aux_orth == '？'` and preserve it instead of converting to `、`
- In `normalize_punctuation` (src/text2accent.py): Changed `text.strip("/、")` to separate operations that don't strip `？`

### Test Results (with ？ preservation)
✓ `元気？大丈夫かな？` → `ゲ'ンキ？ダイジョ'オブカナ？`
✓ `本当に？やった！どう思う？` → `ホントオニ？ヤッタ'、ド'オ/オモ'ウ？`
✓ `テスト。これは？大丈夫！` → `テ'スト、コレワ？ダイジョ'オブ`

## Evaluation Results
Ran `task eval` after modifications:
- **Total edit distance: 96** (improved from baseline 97)
- Test case 5 now correctly preserves `？` at the end
- The modifications slightly improved accuracy while preserving intended punctuation behavior
- All 20 test cases passed
