# run.py
from myapp import create_app, db
from myapp.scheduler import start_scheduler, shutdown_scheduler
import atexit

app = create_app()

with app.app_context():
    db.create_all()

start_scheduler()
atexit.register(lambda: shutdown_scheduler())

if __name__ == '__main__':
    app.run(debug=True)
