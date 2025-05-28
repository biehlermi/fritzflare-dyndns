import os
import logging

logger = logging.getLogger("fritzflare.config")

CF_API_TOKEN = os.environ.get("CF_API_TOKEN")

if not CF_API_TOKEN:
    logger.error("CF_API_TOKEN environment variable not set!")
    exit(1)
