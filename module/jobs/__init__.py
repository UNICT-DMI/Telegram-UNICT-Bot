"""Jobs module"""
from telegram.ext import JobQueue
from module.data import config_map
from .post_and_clear_log import post_and_clear_log_job
from .update_notices import update_notices_job


def add_jobs(job_queue: JobQueue) -> None:
    """Add all the jobs to the job queue.
    They will be called periodically.

    Args:
        job_queue: job queue
    """
    # logfile reset
    job_queue.run_repeating(
        post_and_clear_log_job, interval=config_map["logfile_reset_interval_minutes"] * 60, first=5
    )
    # update tick
    job_queue.run_repeating(update_notices_job, interval=config_map["update_interval"], first=5)
