from django_cron import (
    CronJobBase,
    Schedule
)


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # 1시간마다 실행

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'myapp.my_cron_job'

    def do(self):
        pass
