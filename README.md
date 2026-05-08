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

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/jacobwaynecolton/water-store-social-bot.git
cd water-store-social-bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env` with your API keys. You need:

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) |
| `META_ACCESS_TOKEN` | Meta Developer App (see below) |
| `FACEBOOK_PAGE_ID` | Your Facebook Page's About section or Graph API Explorer |
| `INSTAGRAM_ACCOUNT_ID` | Graph API Explorer — query `me/accounts` then find the linked IG account |

### 3. Meta App setup

1. Go to [developers.facebook.com](https://developers.facebook.com) and create an app (type: **Business**)
2. Add the **Instagram Graph API** and **Pages API** products
3. Generate a **Page Access Token** with these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_comments`
4. Convert it to a long-lived token (valid 60 days) using the token debugger tool
5. Your Instagram account must be a **Business or Creator** account linked to the Facebook Page

### 4. Run the bot

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) to see the dashboard.

The bot starts posting automatically at the times set in `POST_TIMES` (default: 9am, 1pm, 6pm).

## Customizing content

Edit `backend/config.py` to adjust:

- `BUSINESS_DESCRIPTION` — what Claude knows about the business
- `CONTENT_THEMES` — the list of themes it rotates through
- `POST_TIMES` (or set via `.env`) — when posts go out each day

## Running in production

For a persistent deployment (e.g. a VPS or Raspberry Pi):

```bash
# Using systemd or just nohup
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
```

Or use Docker — a `Dockerfile` would be a straightforward addition if needed.

> **Note on Meta tokens:** Page access tokens expire after 60 days. You'll need to refresh the token in `.env` periodically. A cron job to auto-refresh is a possible future improvement.
