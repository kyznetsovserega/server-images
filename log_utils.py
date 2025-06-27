import os
import logging
from logging.handlers import RotatingFileHandler

# --- Настройка ротации логов, формата и кодировки UTF-8 ---
def setup_logging(log_folder='logs', log_filename='app.log', level=logging.INFO):
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, log_filename)

    log_handler = RotatingFileHandler(log_file, maxBytes=2_000_000, encoding='utf-8')
    log_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    log_handler.setFormatter(log_formatter)

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.addHandler(log_handler)
        root_logger.setLevel(level)

# --- Унифицированное логирование для проекта ---
def log_action(message: str, level: str = "info"):
    prefix = {
        "info": "Успех",
        "error": "Ошибка",
        "warning": "Внимание"
    }.get(level.lower(), "Успех")
    if level == "error":
        logging.error(f"{prefix}: {message}")
    elif level == "warning":
        logging.warning(f"{prefix}: {message}")
    else:
        logging.info(f"{prefix}: {message}")
