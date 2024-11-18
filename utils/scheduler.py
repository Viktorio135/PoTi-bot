from dataBase.dump import dump_dict_of_profiles, backup_bd
from utils.reminder import check_activity, unlock_limits, update_love_stat


def start_schedule(scheduler, dict_of_profiles, bot, love_activity):
    scheduler.add_job(dump_dict_of_profiles, 'interval', minutes=30, args=(dict_of_profiles,))
    scheduler.add_job(backup_bd, 'interval', minutes=59)
    scheduler.add_job(check_activity, 'interval', hours=2, args=(dict_of_profiles, bot,))
    scheduler.add_job(unlock_limits, 'interval', hours=1, args=(dict_of_profiles,))
    scheduler.add_job(update_love_stat, 'cron', hour='00', minute='20', args=(love_activity,))

    