# GeekDo Sync

Sync play logs from [BoardGameGeek](https://boardgamegeek.com/) and [RPGGeek](https://rpggeek.com/) to [Grist](https://www.getgrist.com/) for backup and analysis.

## Features

- Incremental sync with automatic overlap detection (only fetches new plays)
- Supports both board game and RPG play data
- Normalized Grist schema with separate tables for plays, items, players, and player-play relationships
- Preserves detailed player data including scores, positions, colors, and ratings

