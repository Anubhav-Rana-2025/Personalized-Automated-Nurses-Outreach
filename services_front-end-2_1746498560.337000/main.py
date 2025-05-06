import functions_framework
from flask import send_file, request
import os

@functions_framework.http
def serve_frontend(request):
    path = request.path.strip("/")
    if path == "" or path == "index.html":
        return send_file("index.html", mimetype="text/html")
    elif path == "style.css":
        return send_file("style.css", mimetype="text/css")
    else:
        return ("Not found", 404)
