# bird_checker

Polls waarneming.nl for bird observations around the locations in `config.json` and
compares them with the life list of `user_id` on waarneming.nl.

Copy `config.example.json` to `config.json` and fill in your waarneming.nl user id and locations.

```bash
uv run python -m bird_checker check    # hourly: prints species that just arrived and aren't on my list
uv run python -m bird_checker weekly   # weekly: species seen in the last 7 days that aren't on my list
```

Both print nothing when there is nothing to report. Observations are stored in `birds.db`
(sqlite), keyed by observation id, so overlapping polls and locations don't duplicate.
The first `check` only fills the database.
