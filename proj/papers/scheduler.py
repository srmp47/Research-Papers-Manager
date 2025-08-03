from apscheduler.schedulers.background import BackgroundScheduler
from Database.mongoDB import transfer_views_to_mongodb

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        transfer_views_to_mongodb,
        'interval',
        minutes=0.5,
        id='transfer_views_job'
    )
    scheduler.start()