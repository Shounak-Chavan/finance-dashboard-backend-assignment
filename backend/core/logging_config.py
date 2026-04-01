import logging
import os


def setup_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # 🔥 create logs folder
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),  # file logs
            logging.StreamHandler()               # console logs
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)