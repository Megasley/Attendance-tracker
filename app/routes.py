import hmac
import logging

from flask import abort, render_template, request, jsonify
from app.sheets import get_bootcamp_participants, verify_access_code
from app import app
from config import Config, event_date_range_text

logging.basicConfig(level=logging.INFO)


def _is_admin(req):
    """True if the request carries the ADMIN_TOKEN (header 'X-Admin-Token' or 'Authorization: Bearer ...')."""
    expected = Config.ADMIN_TOKEN
    if not expected:
        return False
    supplied = req.headers.get('X-Admin-Token', '')
    auth = req.headers.get('Authorization', '')
    if not supplied and auth.lower().startswith('bearer '):
        supplied = auth[7:]
    return hmac.compare_digest(supplied.strip().encode(), expected.encode())


@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        event_city=Config.EVENT_CITY,
        event_dates=event_date_range_text(),
    )

@app.route('/api/participants', methods=['GET'])
def participants():
    # Participant data (names, emails, phones, CVs) is admin-only.
    if not Config.ADMIN_TOKEN:
        abort(404)
    if not _is_admin(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    result = get_bootcamp_participants()
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@app.route('/verify', methods=['POST'])
def verify():
    access_code = (request.form.get('access_code') or '').strip()
    if not access_code:
        return jsonify({'success': False, 'message': 'Please enter your email'})

    result = verify_access_code(access_code)
    return jsonify(result)
