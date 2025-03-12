# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import feedparser
import datetime
from .models import Novel
from . import db

def check_rss_update(novel):
    try:
        print(f"Memeriksa feed: {novel.url}")
        feed = feedparser.parse(novel.url)
        if feed.bozo:
            print(f"Error parsing feed untuk {novel.title}")
            return
        if feed.entries:
            latest_entry = feed.entries[0]
            latest_title = latest_entry.title.strip()
            if latest_title != novel.last_chapter:
                novel.last_chapter = latest_title
                novel.last_update = datetime.datetime.now()
                db.session.commit()
                print(f"Update novel: {novel.title} -> Chapter {novel.last_chapter}")
            else:
                print(f"Tidak ada update baru untuk {novel.title}")
    except Exception as e:
        print(f"Error saat cek RSS feed untuk {novel.title}: {e}")

def update_novels():
    novels = Novel.query.filter_by(approved=True).all()
    for novel in novels:
        check_rss_update(novel)

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_novels, trigger="interval", minutes=10)

def start_scheduler():
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
