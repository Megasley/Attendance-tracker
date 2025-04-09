from flask import render_template, request, jsonify
from app.sheets import verify_access_code
from app import app

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    access_code = request.form.get('access_code')
    if not access_code:
        return jsonify({'success': False, 'message': 'Please enter your email'})
    
    result = verify_access_code(access_code)
    return jsonify(result) 