import logging
from flask import request, jsonify
from app import app
from app.config import CLOUDFLARE_IPV4_ZONES_LIST
from app.cloudflare_api import update_dns_record, InvalidIPAddressError, ZoneNotFoundError, RecordNotFoundError

logger = logging.getLogger("fritzflare.routes")

def validate_update_request(data):
    ipv4 = data.get('ipv4')
    errors = []
    if not ipv4:
        errors.append("Missing 'ipv4'")
    return ipv4, errors

@app.route('/update', methods=['GET'])
def update():
    """
    Update a Cloudflare DNS A record.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.args

    ipv4, errors = validate_update_request(data)
    if errors:
        logger.warning(f"Update request missing parameters: {errors}")
        return jsonify({"status": "error", "message": ", ".join(errors)}), 400

    results = []
    errors = []
    for entry in CLOUDFLARE_IPV4_ZONES_LIST:
        # Determine zone and record
        parts = entry.split('.')
        if len(parts) < 2:
            errors.append(f"Invalid entry: {entry}")
            continue
        zone = '.'.join(parts[-2:])
        if entry == zone:
            record = '@'
        else:
            record = entry[:-(len(zone)+1)]  # Remove ".zone" from the end
        logger.info(f"Updating: zone={zone}, record={record}, ipv4={ipv4}")
        try:
            result = update_dns_record(zone, record, ipv4)
            logger.info(f"DNS record updated: {result}")
            results.append({"zone": zone, "record": record, "result": result})
        except InvalidIPAddressError:
            logger.warning(f"Invalid IPv4 address: {ipv4}")
            errors.append({"zone": zone, "record": record, "error": "Invalid IPv4 address"})
        except ZoneNotFoundError:
            logger.warning(f"Zone not found: {zone}")
            errors.append({"zone": zone, "record": record, "error": "Zone not found"})
        except RecordNotFoundError:
            logger.warning(f"Record not found: {record} in zone {zone}")
            errors.append({"zone": zone, "record": record, "error": "Record not found"})
        except Exception as e:
            logger.exception("Unexpected error during DNS update")
            errors.append({"zone": zone, "record": record, "error": "Internal server error"})
    if errors:
        return jsonify({"status": "partial", "results": results, "errors": errors}), 207
    return jsonify({"status": "success", "results": results}), 200