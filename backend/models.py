import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    theme = Column(String)
    caption = Column(Text)           # we store the Instagram version as canonical
    image_url = Column(String)       # DALL-E URL (expires ~1h, just for reference)
    image_local_path = Column(String)

    facebook_post_id = Column(String, nullable=True)
    instagram_post_id = Column(String, nullable=True)

    # pending → posted or failed
    status = Column(String, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    platform = Column(String)            # "facebook" or "instagram"
    post_id = Column(String)             # our internal post ID (as string)
    comment_id = Column(String, unique=True)
    commenter_name = Column(String)
    comment_text = Column(Text)
    our_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    seen_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/images", exist_ok=True)
    Base.metadata.create_all(bind=engine)
