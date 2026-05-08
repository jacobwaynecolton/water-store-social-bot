import logging
from datetime import datetime, timedelta
from backend.models import SessionLocal, Comment, Post
from backend.meta_api import (
    get_facebook_comments,
    get_instagram_comments,
    reply_to_facebook_comment,
    reply_to_instagram_comment,
)
from backend.content_generator import generate_comment_reply

logger = logging.getLogger(__name__)


def _process_comments(post_db_id: str, platform_post_id: str, platform: str):
    """
    Fetches comments for a single post and replies to any we haven't seen yet.
    We track handled comments by comment_id in the DB to avoid double-replying.
    """
    session = SessionLocal()
    try:
        if platform == "facebook":
            raw_comments = get_facebook_comments(platform_post_id)
        else:
            raw_comments = get_instagram_comments(platform_post_id)

        for raw in raw_comments:
            comment_id = raw.get("id")
            if not comment_id:
                continue

            # Skip comments we've already handled
            if session.query(Comment).filter_by(comment_id=comment_id).first():
                continue

            # Facebook and Instagram have slightly different field names
            if platform == "facebook":
                commenter = raw.get("from", {}).get("name", "Someone")
                text = raw.get("message", "")
            else:
                commenter = raw.get("username", "Someone")
                text = raw.get("text", "")

            if not text.strip():
                continue

            reply = generate_comment_reply(text, commenter)

            if platform == "facebook":
                success = reply_to_facebook_comment(comment_id, reply)
            else:
                success = reply_to_instagram_comment(comment_id, reply)

            session.add(Comment(
                platform=platform,
                post_id=post_db_id,
                comment_id=comment_id,
                commenter_name=commenter,
                comment_text=text,
                our_reply=reply if success else None,
                replied_at=datetime.utcnow() if success else None,
            ))
            session.commit()

            logger.info(f"Replied to {platform} comment from {commenter}")

    except Exception as e:
        logger.error(f"Error processing {platform} comments on post {post_db_id}: {e}")
    finally:
        session.close()


def check_all_recent_comments():
    """
    Scheduled job — checks comments on every post from the last 7 days.
    7 days is enough; posts rarely get new engagement after that.
    """
    session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent = session.query(Post).filter(
            Post.status == "posted",
            Post.posted_at >= cutoff,
        ).all()

        for post in recent:
            if post.facebook_post_id:
                _process_comments(str(post.id), post.facebook_post_id, "facebook")
            if post.instagram_post_id:
                _process_comments(str(post.id), post.instagram_post_id, "instagram")

    finally:
        session.close()
