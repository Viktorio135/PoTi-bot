import schedule
import time
import asyncio


from dataBase.dump import dump_dict_of_profiles, backup_bd
from utils.reminder import check_activity

# async def scheduled_backup_dict_of_profiles_and_reminder(dict_of_profiles, bot):
    # schedule.every(15).minutes.do(dump_dict_of_profiles, dict_of_profiles)
    # schedule.every(20).minutes.do(backup_bd)
    # while True:
    #     schedule.run_pending()
    #     await asyncio.sleep(1)


def start_schedule(scheduler, dict_of_profiles, bot):
    scheduler.add_job(dump_dict_of_profiles, 'interval', seconds=10, args=(dict_of_profiles,))
    scheduler.add_job(backup_bd, 'interval', seconds=10)
    scheduler.add_job(check_activity, 'interval', seconds=10, args=(dict_of_profiles, bot,))
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # asyncio.run(scheduled_backup_dict_of_profiles_and_reminder(dict_of_profiles, bot))