import logging


def create_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
