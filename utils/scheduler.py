from dataBase.dump import dump_dict_of_profiles, backup_bd
from utils.reminder import check_activity


def start_schedule(scheduler, dict_of_profiles, bot):
    scheduler.add_job(dump_dict_of_profiles, 'interval', minutes=30, args=(dict_of_profiles,))
    scheduler.add_job(backup_bd, 'interval', minutes=59)
    scheduler.add_job(check_activity, 'interval', hours=2, args=(dict_of_profiles, bot,))
    