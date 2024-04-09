import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


class LoggerService:
    def __init__(self, log_directory="logs"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{log_directory}/app_{current_date}.log"

        handler = TimedRotatingFileHandler(
            filename=log_file, when="midnight", backupCount=0
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def info(self, message, module = "UndefinedModule"):
        self.logger.info(f"{module} | {message}")

    def warning(self, message, module = "UndefinedModule"):
        self.logger.warning(f"{module} | {message}")

    def error(self, message, module = "UndefinedModule"):
        self.logger.error(f"{module} | {message}")
