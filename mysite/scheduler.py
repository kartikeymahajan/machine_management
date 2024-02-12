from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django.core.management import call_command
from datetime import datetime, timedelta

def send_booking_notifications_job():
    call_command('send_booking_notifications')

def hardware_daily_status():
    call_command('send_hardware_updates')

def trigger_auto_unbook():
    call_command('auto_unbook_machine')

scheduler = BackgroundScheduler()
run_date = datetime.now() + timedelta(minutes=1)
trigger = DateTrigger(run_date=run_date)
scheduler.add_job(send_booking_notifications_job, 'interval', minutes = 1)
# 'cron' style scheduling to run every day at 8:00 AM. You can adjust the time as needed.
scheduler.add_job(hardware_daily_status, 'cron', hour=20, minute=16)
scheduler.add_job(trigger_auto_unbook, 'interval', minutes = 1)

scheduler.start()