import datetime
from copy import deepcopy

from pythonjsonlogger import jsonlogger


class ELKJsonFormatter(jsonlogger.JsonFormatter):
    def _filter_log(self, data: dict):
        if data and isinstance(data, dict):
            for key, value in data.copy().items():
                if isinstance(key, bytes):
                    data.pop(key)
                    key = key.decode("utf-8")
                    data[key] = value
                if isinstance(value, bytes):
                    value = value.decode("utf-8")
                    data[key] = value
                if isinstance(value, dict):
                    data[key] = self._filter_log(value)
        return data

    def add_fields(self, log_record, record, message_dict):
        super(ELKJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["log_time"] = datetime.datetime.now(tz=datetime.timezone.utc)
        if isinstance(record.msg, dict):
            log_record["scope"] = self._filter_log(deepcopy(record.msg.get("scope")))
            log_record["content"] = self._filter_log(deepcopy(record.msg.get("content")))


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "core.logging.ELKJsonFormatter"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "uvicorn": {"handlers": [], "level": "INFO"},
        "gunicorn": {"handlers": ["console"], "level": "INFO"},
        "gunicorn.access": {"handlers": ["console"], "level": "INFO"},
        "gunicorn.error": {"handlers": ["console"], "level": "INFO"},
        "django": {"handlers": ["console"], "level": "INFO"},
        "channels": {"handlers": ["console"], "level": "INFO"},
    },
}
