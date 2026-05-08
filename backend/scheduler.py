import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.config import POST_TIMES, COMMENT_CHECK_INTERVAL, DRY_RUN, THEME_LOOKBACK
from backend.models import SessionLocal, Post, init_db
from backend.content_generator import pick_theme, generate_post_content
from backend.image_generator import get_image_for_post
from backend.meta_api import post_to_facebook, post_to_instagram
from backend.comment_responder import check_all_recent_comments

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def run_posting_job():
    """
    The main event: pick a theme → generate captions + image → post to both platforms.
    Everything is written to the DB first so failures are visible on the dashboard.
    """
    session = SessionLocal()
    record = Post(status="pending")
    session.add(record)
    session.commit()

    try:
        # Look back at recent posts so we don't repeat a similar theme too soon
        recent_themes = [
            r.theme for r in session.query(Post.theme)
            .filter(Post.theme.isnot(None))
            .order_by(Post.created_at.desc())
            .limit(THEME_LOOKBACK)
            .all()
        ]
        theme = pick_theme(recent_themes)
        logger.info(f"Starting post job | theme: {theme} | avoided: {recent_themes}")
        record.theme = theme
        session.commit()

        # Pass recent themes so Claude writes something that feels different, not just a different label
        content = generate_post_content(theme, recent_themes)
        record.caption = content.get("instagram", "")
        session.commit()

        # Prefer a real site photo; fall back to a DALL-E illustration if none match the theme
        public_url, local_path = get_image_for_post(theme, content["image_prompt"])
        record.image_url = public_url
        record.image_local_path = local_path
        session.commit()

        if DRY_RUN:
            # Skip Meta API calls — just mark as posted so the dashboard shows the result
            record.status = "posted"
            record.posted_at = datetime.utcnow()
            record.facebook_post_id = "dry-run"
            record.instagram_post_id = "dry-run"
            session.commit()
            logger.info(f"DRY RUN — post generated but not published | image: {local_path}")
        else:
            # Publish — order doesn't matter, but do Facebook first since it's more forgiving
            record.facebook_post_id = post_to_facebook(content["facebook"], dalle_url)
            record.instagram_post_id = post_to_instagram(content["instagram"], dalle_url)

            record.status = "posted"
            record.posted_at = datetime.utcnow()
            session.commit()

            logger.info(f"Post live | FB: {record.facebook_post_id} | IG: {record.instagram_post_id}")

    except Exception as e:
        record.status = "failed"
        record.error_message = str(e)
        session.commit()
        logger.error(f"Post job failed: {e}")

    finally:
        session.close()


def start_scheduler():
    """Register all jobs and start the scheduler. Called once at server startup."""
    init_db()

    for time_str in POST_TIMES:
        hour, minute = time_str.strip().split(":")
        scheduler.add_job(
            run_posting_job,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id=f"post_{time_str}",
            replace_existing=True,
        )
        logger.info(f"Scheduled post at {time_str} daily")

    scheduler.add_job(
        check_all_recent_comments,
        trigger="interval",
        minutes=COMMENT_CHECK_INTERVAL,
        id="comment_check",
        replace_existing=True,
    )
    logger.info(f"Comment check every {COMMENT_CHECK_INTERVAL} minutes")


    scheduler.start()
    return scheduler
