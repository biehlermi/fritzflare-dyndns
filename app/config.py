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

CLOUDFLARE_DNS_HOSTNAMES = os.environ.get("CLOUDFLARE_DNS_HOSTNAMES")
logger.info(f"CLOUDFLARE_DNS_HOSTNAMES raw value: {CLOUDFLARE_DNS_HOSTNAMES}")

if not CLOUDFLARE_DNS_HOSTNAMES:
    logger.error("Required environment variable CLOUDFLARE_DNS_HOSTNAMES is not set!")
    exit(1)

# Parse the hostnames as a list, stripping whitespace and ignoring empty entries
CLOUDFLARE_DNS_HOSTNAMES_LIST = [z.strip() for z in CLOUDFLARE_DNS_HOSTNAMES.split(',') if z.strip()]
logger.info(f"Parsed CLOUDFLARE_DNS_HOSTNAMES_LIST: {CLOUDFLARE_DNS_HOSTNAMES_LIST}")