# Fedi post purger

Mass-delete posts from any mastodon-api compatible instance

Usage:

copy `fedi.login.example` to `fedi.example` and fill in your details

```bash
pipenv run python run.py --from-date YYYY-MM-DD --to-date YYYY-MM-DD --public-only
```

Options:

- `--from-date` the date of the first post you want to purge
- `--to-date` the date of the last post you want to purge
- `--public-only` limit deletion to posts with visibility of `public` or `unlisted`
