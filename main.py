"""Main module"""
import logging
from telegram.ext import Updater
from module.data import config_map
from module.handlers import add_handlers, add_jobs


def setup_logging(logs_file: str) -> None:
    """Sets up the logging system.
    Creates a file handler and a stream handler.

    Args:
        logs_file: path to the log file
    """
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()

    file_handler = logging.FileHandler(f"{logs_file}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.INFO)


def main() -> None:
    """Main function"""
    setup_logging("logfile")
    logging.info("Initialization...")

    updater = Updater(config_map["token"])
    add_handlers(updater.dispatcher)
    add_jobs(updater.job_queue)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
