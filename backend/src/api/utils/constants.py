LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": "uvicorn.logging.ColourizedFormatter",
            "format": "%(levelprefix)-8s %(name)s: %(message)s",
        },
        "executor": {
            "()": "uvicorn.logging.ColourizedFormatter",
            "format": "%(levelprefix)-8s [%(device)s](%(process)d) :: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "executor": {
            "level": "INFO",
            "formatter": "executor",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
        "api": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "api.compute.executor": {
            "handlers": ["executor"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
