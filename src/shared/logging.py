import logging
import sys

def setup_logging(service_name: str = "cat-sys"):
    logger = logging.getLogger(service_name)
    handler = logging.StreamHandler(sys.stdout)
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
