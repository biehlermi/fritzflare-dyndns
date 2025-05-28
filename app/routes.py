import logging
from flask import request, jsonify
from app import app
from app.cloudflare_api import update_dns_record, InvalidIPAddressError, ZoneNotFoundError, RecordNotFoundError

logger = logging.getLogger("fritzflare.routes")

def validate_update_request(data):
    zone = data.get('zone')
    record = data.get('record')
    ipv4 = data.get('ipv4')
    errors = []
    if not zone:
        errors.append("Missing 'zone'")
    if not record:
        errors.append("Missing 'record'")
    if not ipv4:
        errors.append("Missing 'ipv4'")
    return zone, record, ipv4, errors

@app.route('/update', methods=['GET'])
def update():
    """
    Update a Cloudflare DNS A record.
    Expects JSON: { "zone": "...", "record": "...", "ipv4": "..." }
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.args

    zone, record, ipv4, errors = validate_update_request(data)
    if errors:
        logger.warning(f"Update request missing parameters: {errors}")
        return jsonify({"status": "error", "message": ", ".join(errors)}), 400

    logger.info(f"Received update request: zone={zone}, record={record}, ipv4={ipv4}")

    try:
        result = update_dns_record(zone, record, ipv4)
        logger.info(f"DNS record updated: {result}")
        return jsonify({"status": "success", "message": result}), 200
    except InvalidIPAddressError:
        logger.warning(f"Invalid IPv4 address: {ipv4}")
        return jsonify({"status": "error", "message": "Invalid IPv4 address"}), 400
    except ZoneNotFoundError:
        logger.warning(f"Zone not found: {zone}")
        return jsonify({"status": "error", "message": "Zone not found"}), 404
    except RecordNotFoundError:
        logger.warning(f"Record not found: {record} in zone {zone}")
        return jsonify({"status": "error", "message": "Record not found"}), 404
    except Exception as e:
        logger.exception("Unexpected error during DNS update")
        return jsonify({"status": "error", "message": "Internal server error"}), 500