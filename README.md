# SF Adventures

A catalog of San Francisco (and beyond) adventures for two, plus a "what should we do today?" draw mechanic. Home base: Pacific Heights, near Polk Gulch.

## Structure

```
data/activities.json   # source of truth — every activity + the deck config
scripts/gen_catalog.py # regenerates preview/catalog.html (browse & filter)
scripts/gen_today.py   # regenerates preview/today.html (the daily draw)
preview/               # generated, self-contained HTML previews (open in a browser)
```

Regenerate the previews after editing the data:

```bash
python3 scripts/gen_catalog.py
python3 scripts/gen_today.py
```

## Activity schema

Each entry in `data/activities.json → activities[]`:

| field | meaning |
|---|---|
| `id` | kebab-case unique slug |
| `name`, `description` | display name + why it's a fun outing |
| `category` | Outdoorsy & scenic · Food & drink · Arts & culture · Playful & active |
| `neighborhood` | area, for clustering nearby things |
| `cost` / `costLevel` | `Free`–`$$$$` / `0`–`4` |
| `duration` / `durationRank` | `1hr`·`4hr`·`all-day`·`multi-day` / `1`–`4` |
| `scope` | `in-city` · `day-trip` · `getaway` |
| `nearHome` | within the Pac Heights / Polk Gulch orbit |
| `season` | e.g. `Year-round`, `Apr–Oct` |
| `withFriends` | good as a group / double date |
| `logistics` | indoor/outdoor, weather, reservation, dog-friendly, getting there |
| `tags`, `pairsWith` | filter tags · ids of nearby activities that combine into a day |
| `stops` | crawls only: ordered `{name, note}` route |

## The "today" draw — a cooldown deck

`meta.deck` in the data file holds the rules:

- Pick a time budget → draw one random eligible card (without replacement).
- **Did it** → the card rests for a duration-based cooldown, then returns to the pool:
  ~1hr → 2 weeks · ~4hr → 1 month · all-day → 1 quarter · multi-day → 1 year.
- **Skip** → the card rests briefly (a few days to a month), then returns — so skipping never burns the deck.

The preview persists your deck state in the browser (`localStorage`); a real app would move that to a shared account so both people see the same deck.
