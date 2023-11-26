import logging


def create_logger(name: str, level=logging.INFO, tag="fb-poster") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(tag)s] %(name)s %(levelname)s: %(message)s"
    )

    # Tworzenie niestandardowego filtra dodającego tag do logów
    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.tag = tag
            return True

    log_filter = ContextFilter()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(log_filter)  # Dodawanie filtra do handlera
    logger.addHandler(console_handler)
    return logger
