# water-store-social-bot

Autonomous social media bot for [Water Store OS](https://waterstoreos.ca). Runs 24/7, generates and posts original content to Facebook and Instagram on a schedule, and automatically replies to comments — no manual input needed.

## What it does

- **Generates posts** — Uses Claude to write platform-specific captions based on rotating content themes (product spotlights, hydration tips, water quality education, seasonal promos, etc.)
- **Generates images** — Uses DALL-E 3 to create a matching image for every post
- **Cross-posts** — Publishes to both Facebook Page and Instagram Business account simultaneously
- **Replies to comments** — Polls for new comments every 30 minutes and generates on-brand replies via Claude
- **Web dashboard** — Simple browser UI to monitor post history, comment log, scheduled jobs, and manually trigger a post

## Project structure

```
water-store-bot/
├── backend/
│   ├── main.py                # FastAPI app and dashboard API
│   ├── scheduler.py           # APScheduler — drives posting and comment jobs
│   ├── content_generator.py   # Claude API — captions, image prompts, comment replies
│   ├── image_generator.py     # DALL-E 3 — image generation
│   ├── meta_api.py            # Meta Graph API — Facebook + Instagram
│   ├── comment_responder.py   # Comment polling and auto-reply logic
│   ├── models.py              # SQLAlchemy models (posts, comments)
│   └── config.py              # Config and constants loaded from .env
├── frontend/
│   ├── index.html             # Dashboard UI
│   ├── app.js                 # Dashboard JS
│   └── style.css              # Dashboard styles
├── data/                      # SQLite DB + saved images (git-ignored)
├── .env.example               # Template — copy to .env and fill in
└── requirements.txt
```

## Customizing content

Edit `backend/config.py` to adjust:

- `BUSINESS_DESCRIPTION` — what Claude knows about the business
- `CONTENT_THEMES` — the list of themes it rotates through
- `POST_TIMES` (or set via `.env`) — when posts go out each day

