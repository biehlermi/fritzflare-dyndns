import logging
import ipaddress
from typing import Optional
from app.config import CLOUDFLARE_API_TOKEN
from cloudflare import Cloudflare

logger = logging.getLogger("fritzflare.cloudflare_api")

class ZoneNotFoundError(Exception):
    pass

class RecordNotFoundError(Exception):
    pass

class InvalidIPAddressError(Exception):
    pass

def validate_ipv4_address(ip: str) -> None:
    """Raise InvalidIPAddressError if ip is not a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise InvalidIPAddressError(f"'{ip}' is not a valid IPv4 address.")

def get_zone_id(client: Cloudflare, zone_name: str) -> str:
    zones = list(client.zones.list(name=zone_name))
    if not zones:
        raise ZoneNotFoundError(f"Zone '{zone_name}' not found.")
    return zones[0].id

def get_a_record(client: Cloudflare, zone_id: str, fqdn: str) -> object:
    records = list(client.dns.records.list(zone_id=zone_id, name=fqdn, type="A"))
    if not records:
        raise RecordNotFoundError(f"A record '{fqdn}' not found in zone.")
    return records[0]

def update_dns_record(
    zone_name: str,
    record_name: str,
    new_ip: str,
    client: Optional[Cloudflare] = None
) -> str:
    """
    Update an existing A-Record in Cloudflare.
    If record_name == '@', the zone name is used as the record name.
    """
    logger.info(f"Request to update DNS record: zone={zone_name}, record={record_name}, new_ip={new_ip}")

    if not zone_name or not record_name or not new_ip:
        logger.error("Missing required parameters.")
        raise ValueError("zone_name, record_name, and new_ip are required.")

    validate_ipv4_address(new_ip)

    if client is None:
        client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

    fqdn = zone_name

    try:
        zone_id = get_zone_id(client, zone_name)
        record = get_a_record(client, zone_id, fqdn)

        _ = client.dns.records.update(
            dns_record_id=record.id,
            zone_id=zone_id,
            type="A",
            name=fqdn,
            content=new_ip,
            ttl=record.ttl,
            proxied=record.proxied
        )
        logger.info(f"Record {fqdn} updated to {new_ip}")
        return f"Record {fqdn} updated to {new_ip}"
    except (ZoneNotFoundError, RecordNotFoundError, InvalidIPAddressError) as e:
        logger.warning(str(e))
        raise
    except Exception as e:
        logger.exception("Unexpected error during DNS record update")
        raise RuntimeError("Failed to update DNS record due to an internal error.") from e