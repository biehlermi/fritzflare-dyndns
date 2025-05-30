import os
import logging
from pathlib import Path

# Load .env.development if it exists (for testing)
try:
    from dotenv import load_dotenv
    dev_env = Path(__file__).parent.parent / ".env.development"
    if dev_env.exists():
        load_dotenv(dotenv_path=dev_env)
except ImportError:
    pass

logger = logging.getLogger("fritzflare.config")

CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
logger.info(f"CLOUDFLARE_API_TOKEN set: {'YES' if CLOUDFLARE_API_TOKEN else 'NO'}")

if not CLOUDFLARE_API_TOKEN:
    logger.error("Required environment variable CLOUDFLARE_API_TOKEN is not set!")
    exit(1)

CLOUDFLARE_IPV4_ZONES = os.environ.get("CLOUDFLARE_IPV4_ZONES")
logger.info(f"CLOUDFLARE_IPV4_ZONES raw value: {CLOUDFLARE_IPV4_ZONES}")

if not CLOUDFLARE_IPV4_ZONES:
    logger.error("Required environment variable CLOUDFLARE_IPV4_ZONES is not set!")
    exit(1)

# Parse the zones as a list, stripping whitespace and ignoring empty entries
CLOUDFLARE_IPV4_ZONES_LIST = [z.strip() for z in CLOUDFLARE_IPV4_ZONES.split(',') if z.strip()]
logger.info(f"Parsed CLOUDFLARE_IPV4_ZONES_LIST: {CLOUDFLARE_IPV4_ZONES_LIST}")