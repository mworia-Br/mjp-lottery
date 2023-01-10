# tasks.py
from celery.decorators import task, periodic_task

@task
def daily_draw():
    # Code to run the daily draw
    pass

@periodic_task(run_every=(crontab(hour=20, minute=15)), name="daily_draw_task")
def scheduled_daily_draw():
    daily_draw.delay()
