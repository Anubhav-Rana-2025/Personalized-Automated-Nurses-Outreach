import functions_framework
from flask import request, jsonify, make_response
import csv
import io

@functions_framework.http
def upload(request):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
        return response

    
    if request.method != 'POST':
        return 'Only POST allowed', 405

    file = request.files.get('file')
    if not file:
        return 'File missing', 400

    
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.reader(stream)
    data = list(reader)

    if not data:
        return jsonify({'headers': [], 'rows': []})

    headers = data[0]
    rows = data[1:]

    
    response = jsonify({'headers': headers, 'rows': rows})
    response.headers.set('Access-Control-Allow-Origin', '*')
    return response
