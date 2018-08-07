# pylint: disable=wildcard-import, unused-wildcard-import
from .default import *

CONFIG_NAME = "dev"

# redis
REDIS_URL = "redis://localhost:6379/0"

# cache
CACHE_REDIS_URL = REDIS_URL
