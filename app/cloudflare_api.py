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

def update_dns_records(
    zone_name: str,
    record_name: str,
    new_ipv4: Optional[str] = None,
    new_ipv6: Optional[str] = None,
    ipv6lanprefix: Optional[str] = None,
    client: Optional[Cloudflare] = None
) -> dict:
    """
    Update A and/or AAAA records in Cloudflare with as few API calls as possible.
    Returns a dict with results for 'A' and/or 'AAAA'.
    """
    logger.info(f"Request to update DNS records: zone={zone_name}, record={record_name}, new_ipv4={new_ipv4}, new_ipv6={new_ipv6}, ipv6lanprefix={ipv6lanprefix}")

    if not zone_name or not record_name or (not new_ipv4 and not new_ipv6 and not (ipv6lanprefix and new_ipv6)):
        logger.error("Missing required parameters.")
        raise ValueError("zone_name, record_name, and at least one of new_ipv4, new_ipv6, or both ipv6lanprefix and new_ipv6 are required.")

    if client is None:
        client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

    fqdn = zone_name
    zone_id = get_zone_id(client, zone_name)
    # Fetch all records for this fqdn in one call
    records = list(client.dns.records.list(zone_id=zone_id, name=fqdn))
    result = {}

    if new_ipv4:
        validate_ipv4_address(new_ipv4)
        a_record = next((r for r in records if r.type == "A"), None)
        if not a_record:
            raise RecordNotFoundError(f"A record '{fqdn}' not found in zone.")
        _ = client.dns.records.update(
            dns_record_id=a_record.id,
            zone_id=zone_id,
            type="A",
            name=fqdn,
            content=new_ipv4,
            ttl=a_record.ttl,
            proxied=a_record.proxied
        )
        logger.info(f"A Record {fqdn} updated to {new_ipv4}")
        result["A"] = f"A Record {fqdn} updated to {new_ipv4}"

    if new_ipv6 or (ipv6lanprefix and new_ipv6):
        # If both ipv6lanprefix and new_ipv6 are provided, combine them. Otherwise, use new_ipv6 as the full address.
        if ipv6lanprefix and new_ipv6:
            prefix = ipv6lanprefix.split('/')[0]
            if not prefix.endswith(':') and not prefix.endswith('::'):
                if prefix.count(':') < 7:
                    prefix += ':'
            if prefix.endswith('::') and new_ipv6.startswith(':'):
                ipv6_to_use = prefix + new_ipv6[1:]
            elif prefix.endswith(':') and new_ipv6.startswith(':'):
                ipv6_to_use = prefix + new_ipv6[1:]
            elif prefix.endswith(':') or prefix.endswith('::'):
                ipv6_to_use = prefix + new_ipv6
            else:
                ipv6_to_use = prefix + ':' + new_ipv6.lstrip(':')
        else:
            ipv6_to_use = new_ipv6
        validate_ipv6_address(ipv6_to_use)
        aaaa_record = next((r for r in records if r.type == "AAAA"), None)
        if not aaaa_record:
            raise RecordNotFoundError(f"AAAA record '{fqdn}' not found in zone.")
        _ = client.dns.records.update(
            dns_record_id=aaaa_record.id,
            zone_id=zone_id,
            type="AAAA",
            name=fqdn,
            content=ipv6_to_use,
            ttl=aaaa_record.ttl,
            proxied=aaaa_record.proxied
        )
        logger.info(f"AAAA Record {fqdn} updated to {ipv6_to_use}")
        result["AAAA"] = f"AAAA Record {fqdn} updated to {ipv6_to_use}"

    return result

def validate_ipv4_address(ip: str) -> None:
    """Raise InvalidIPAddressError if ip is not a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise InvalidIPAddressError(f"'{ip}' is not a valid IPv4 address.")

def validate_ipv6_address(ip: str) -> None:
    """Raise InvalidIPAddressError if ip is not a valid IPv6 address."""
    try:
        ipaddress.IPv6Address(ip)
    except ValueError:
        raise InvalidIPAddressError(f"'{ip}' is not a valid IPv6 address.")


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
