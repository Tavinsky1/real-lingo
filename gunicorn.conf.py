# Gunicorn configuration for LingoWorld
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/slanglingo_access.log"
errorlog = "/var/log/gunicorn/slanglingo_error.log"
loglevel = "info"

# Process naming
proc_name = 'slanglingo'

# Server mechanics
daemon = False
pidfile = '/var/run/gunicorn/slanglingo.pid'
user = "www-data"
group = "www-data"

# SSL (if needed)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/certificate.crt"
