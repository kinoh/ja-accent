# Decisions

- Flush the current accent phrase when a punctuation token with a phrase boundary flag is encountered, even if it has no pronunciation.
- Attach boundary punctuation (e.g., exclamation/question marks) to the preceding phrase so it does not form a standalone accent phrase.

# User Feedback

- The user reported that exclamation marks were not treated as boundaries and question marks formed their own phrase; the logic now flushes on boundary punctuation to keep the intended segmentation.
