import logging
from flask import request, jsonify
from app import app
from app.config import CLOUDFLARE_DNS_HOSTNAMES_LIST
from app.cloudflare_api import update_dns_records, InvalidIPAddressError, ZoneNotFoundError, RecordNotFoundError

logger = logging.getLogger("fritzflare.routes")

def validate_update_request(data):
    ipv4 = data.get('ipv4')
    ipv6 = data.get('ipv6')
    ipv6lanprefix = data.get('ipv6lanprefix')
    errors = []
    if not ipv4 and not ipv6 and not (ipv6lanprefix and ipv6):
        errors.append("At least one of 'ipv4', 'ipv6', or both 'ipv6lanprefix' and 'ipv6' must be provided")
    return ipv4, ipv6, ipv6lanprefix, errors

@app.route('/update', methods=['GET'])
def update():
    """
    Update a Cloudflare DNS A and/or AAAA record.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.args

    ipv4, ipv6, ipv6lanprefix, errors = validate_update_request(data)
    if errors:
        logger.warning(f"Update request missing parameters: {errors}")
        return jsonify({"status": "error", "message": ", ".join(errors)}), 400
    
    results = []
    errors = []
    updated = False
    nochg = False
    for entry in CLOUDFLARE_DNS_HOSTNAMES_LIST:
        # Determine zone and record
        parts = entry.split('.')
        if len(parts) < 2:
            return ("nohost", 200, {"Content-Type": "text/plain"})
        zone = '.'.join(parts[-2:])
        if entry == zone:
            record = '@'
        else:
            record = entry[:-(len(zone)+1)]  # Remove ".zone" from the end
        try:
            result = update_dns_records(zone, record, ipv4, ipv6, ipv6lanprefix=ipv6lanprefix)
            if result.get("A") or result.get("AAAA"):
                updated = True
            else:
                nochg = True
        except InvalidIPAddressError as e:
            logger.warning(str(e))
            return ("badagent", 200, {"Content-Type": "text/plain"})
        except ZoneNotFoundError:
            logger.warning(f"Zone not found: {zone}")
            return ("nohost", 200, {"Content-Type": "text/plain"})
        except RecordNotFoundError as e:
            logger.warning(str(e))
            return ("nohost", 200, {"Content-Type": "text/plain"})
        except Exception as e:
            logger.exception("Unexpected error during DNS update")
            return ("911", 200, {"Content-Type": "text/plain"})
    if updated:
        return ("good", 200, {"Content-Type": "text/plain"})
    if nochg:
        return ("nochg", 200, {"Content-Type": "text/plain"})
    return ("911", 200, {"Content-Type": "text/plain"})