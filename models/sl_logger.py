import logging
from logging.handlers import RotatingFileHandler
import yaml
from pathlib import Path


class SlLogger:
    home = str(Path.home())
    log_level = " "
    try:
        with open(home + "/config.yaml", 'r') as yamlfile:
            cfg = yaml.load(yamlfile)
            log_level = cfg['log_level']
    except Exception:
        raise Exception("Please specify log level")

    @classmethod
    def get_logger(cls, name):
        logger = logging.getLogger(name)
        handler = RotatingFileHandler('sl_app.log', mode='a', maxBytes=20*1024*1024, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(pathname)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        if cls.log_level == "debug" or "DEBUG":
            logger.setLevel(logging.DEBUG)
        if cls.log_level == "info" or "INFO":
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
        if logger.name == "netmiko" and logger.name == "paramiko.transport":
            logger.setLevel(logging.CRITICAL + 1)
        logger.addHandler(handler)
        return logger
