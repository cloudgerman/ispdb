import argparse
import logging
import logging.config


def logs(params: argparse.Namespace) -> None:
    format = "%(message)s"
    level = (params.debug and logging.DEBUG) or logging.INFO

    conf = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {"standard": {"format": format}},
        "handlers": {
            "console": {
                "level": level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "ispdb": {"level": level},
        },
        "root": {"level": "CRITICAL", "handlers": ["console"]},
    }
    logging.config.dictConfig(conf)
