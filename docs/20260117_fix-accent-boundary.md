# Decisions

- Preserved the accent phrase boundary when inserting standalone long vowel marks so later normalization does not merge phrases.
- Implemented a targeted guard for auxiliary symbols (`ー`) that would otherwise remove the `/` boundary and create multiple accent nuclei in a single phrase.

# User Feedback

- The user reported multiple accent marks appearing in a single accent phrase for input "元気だよ～君は元気？"; the fix above addresses this by keeping the phrase boundary intact.
