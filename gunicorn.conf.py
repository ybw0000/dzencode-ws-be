import multiprocessing

from core.logging import LOGGING

workers_per_core = 2
cores = multiprocessing.cpu_count()
default_web_concurrency = workers_per_core * cores
web_concurrency = max(int(default_web_concurrency), 2)


# Gunicorn config variables
bind = "0.0.0.0:8000"
workers = web_concurrency
worker_class = "core.workers.UvicornWorker"
graceful_timeout = 300  # default
timeout = 300  # default
keepalive = 2  # default
logconfig_dict = LOGGING

# For debugging and testing
log_data = {
    "message": "GUNICORN CONFIG LOADED",
    "workers_per_core": workers_per_core,
    "cores": cores,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
}
