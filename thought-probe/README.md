# Thought Probe — Attentional Distraction Measurement Tool

A Python/tkinter desktop application for a physiological computing research
study measuring attentional distraction during reading tasks.  Presents reading
passages, randomly interrupts with attention-rating thought probes, and logs all
events with millisecond-precision timestamps to a CSV file.

## Requirements

- **Python 3.6+** (standard library only — no external packages needed)

## Quick Start

```bash
python main.py
```

For a compressed-timing test that runs the full flow in ~2 minutes:

```bash
python main.py --test
```

## Application Flow

1. **STARTUP** — enter participant ID, select condition (feedback/no-feedback),
   and choose passage order (A then B, or B then A)
2. **INSTRUCTIONS** — brief instructions then "Start Reading"
3. **READING** (25 min) — scrollable passage text with:
   - Random thought probes every 60–90 seconds
   - A self-caught "I notice my mind wandering" button
   - Visible countdown timer
4. **QUIZ** — 7 multiple-choice comprehension questions (one at a time)
5. **BREAK** — rest screen; continue to the second passage or questionnaire
6. Repeat steps 2–5 for the second passage
7. **ACCEPTABILITY QUESTIONNAIRE** — 5 Likert-scale items (1–5)
8. **END** — thank-you screen with data file path

## Editing Content

All passage text, quiz questions, and answer keys are in **`content.py`**.
Edit the `PASSAGES` dictionary — the main application logic does **not** need
to be touched when changing reading content.

### Structure

```python
PASSAGES = {
    "A": {
        "title": "My Passage Title",
        "text": "Full passage text...",
        "questions": [
            {
                "id": "A1",
                "question": "Question text?",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct_index": 2   # 0-based index of right answer
            },
            # ... 7 total questions
        ],
    },
    "B": {
        # same structure
    },
}
```

The `QUESTIONNAIRE_ITEMS` list and `QUESTIONNAIRE_ITEM_LABELS` dict can also be
edited in `content.py`.

## Data Files

Session data is written to `data/session_{participant_id}_{unix_timestamp}.csv`.

### Columns

| Column       | Description                                          |
|--------------|------------------------------------------------------|
| `event_type`    | Type of event (see below)                         |
| `timestamp_ms`  | Wall-clock time in ms since Unix epoch             |
| `condition`     | Feedback condition (`feedback` / `no_feedback`)    |
| `passage_id`    | Passage identifier (`A` / `B`)                     |
| `value`         | Primary value (probe rating, quiz answer, etc.)    |
| `extra`         | Supplementary metadata                             |

### Event Types

| Event                  | Description                                      |
|------------------------|--------------------------------------------------|
| `SESSION_START`        | Session began, with condition and order in extra |
| `READING_START`        | Reading phase began                              |
| `PROBE_SHOWN`          | Thought probe interruption appeared              |
| `PROBE_RESPONSE`       | Participant responded to probe (value = 1–4)     |
| `SELF_CAUGHT`          | Participant clicked self-caught button           |
| `READING_END`          | Reading phase completed (25 min elapsed)         |
| `QUIZ_ANSWER`          | Quiz question answered (value = selected index)  |
| `QUESTIONNAIRE_ANSWER` | Post-session Likert response (value = 1–5)       |
| `SESSION_END`          | Session completed cleanly                        |
| `SESSION_ABORTED`      | Session aborted by experimenter                  |

Rows are flushed to disk immediately after each write so partial data is
preserved if the program crashes.

## Admin / Safety Features

- **Escape-hold abort**: Hold the **Escape** key for 2 seconds to abort the
  session. A confirmation dialog will appear.
- **Admin exit button**: A small clock icon (🕐) in the bottom-right corner of
  the window performs the same abort function.
- **Window close**: Closing the window during an active session prompts for
  confirmation before aborting.

## Test Mode

```bash
python main.py --test
```

Compresses all timing for rapid testing (no need to wait 25 minutes):

| Parameter          | Normal    | Test       |
|--------------------|-----------|------------|
| Reading duration   | 25 min    | 30 seconds |
| Probe interval     | 60–90 s   | 3–5 s      |

The full flow (2 reading blocks + quiz + questionnaire) completes in ~2 minutes.
A red `[TEST MODE]` indicator appears on the startup and instruction screens.
