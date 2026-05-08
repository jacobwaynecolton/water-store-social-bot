import logging
import os
import threading
from contextlib import asynccontextmanager
from sqlalchemy import desc
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.scheduler import start_scheduler, scheduler, run_posting_job
from backend.models import SessionLocal, Post, Comment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(title="Water Store Social Bot", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
# Serve generated images and any real photos dropped into approved_photos/
os.makedirs("data/images", exist_ok=True)
os.makedirs("data/approved_photos", exist_ok=True)
app.mount("/images", StaticFiles(directory="data/images"), name="images")
app.mount("/approved-photos", StaticFiles(directory="data/approved_photos"), name="approved-photos")
templates = Jinja2Templates(directory="frontend")


def _image_url(local_path: str | None) -> str | None:
    if not local_path:
        return None
    filename = os.path.basename(local_path)
    if "approved_photos" in local_path:
        return f"/approved-photos/{filename}"
    return f"/images/{filename}"


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/posts")
async def get_posts(limit: int = 20):
    session = SessionLocal()
    try:
        posts = session.query(Post).order_by(desc(Post.created_at)).limit(limit).all()
        return [
            {
                "id": p.id,
                "theme": p.theme,
                "caption": p.caption,
                "status": p.status,
                "error": p.error_message,
                "facebook_post_id": p.facebook_post_id,
                "instagram_post_id": p.instagram_post_id,
                "posted_at": p.posted_at.isoformat() if p.posted_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                # Build a URL the browser can fetch — route depends on where the file lives
                "image_url": _image_url(p.image_local_path),
                "image_source": "approved" if (p.image_local_path and "approved_photos" in p.image_local_path) else "generated",
            }
            for p in posts
        ]
    finally:
        session.close()


@app.get("/api/comments")
async def get_comments(limit: int = 50):
    session = SessionLocal()
    try:
        comments = session.query(Comment).order_by(desc(Comment.seen_at)).limit(limit).all()
        return [
            {
                "id": c.id,
                "platform": c.platform,
                "commenter": c.commenter_name,
                "comment": c.comment_text,
                "reply": c.our_reply,
                "replied_at": c.replied_at.isoformat() if c.replied_at else None,
            }
            for c in comments
        ]
    finally:
        session.close()


@app.get("/api/status")
async def get_status():
    jobs = [
        {
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        }
        for job in scheduler.get_jobs()
    ]
    return {"running": scheduler.running, "jobs": jobs}


@app.post("/api/post-now")
async def post_now():
    """Kick off a post immediately — useful for testing from the dashboard."""
    thread = threading.Thread(target=run_posting_job, daemon=True)
    thread.start()
    return {"message": "Post job started"}


@app.post("/api/pause")
async def pause_scheduler():
    scheduler.pause()
    return {"status": "paused"}


@app.post("/api/resume")
async def resume_scheduler():
    scheduler.resume()
    return {"status": "running"}
