from flask import Flask, jsonify, send_from_directory, render_template
from flask import send_from_directory, redirect, request
from flask.helpers import send_file
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.exceptions import abort
import os
from models import mongo
import dns
import json
from config import url
from flask.json import JSONEncoder
class CustomJsonEncoder(JSONEncoder):
    def default(self, o):
        from bson.objectid import ObjectId
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

app = Flask(__name__, )
app.json_encoder=CustomJsonEncoder
app.config['JSON_AS_ASCII'] = False
CORS(app)
app.config["MONGO_URI"] = url
mongo.init_app(app)
bcrypt = Bcrypt(app)
app.config["bcrypt"] = bcrypt

from routes import *
import webpush.main as webpush
app.register_blueprint(routes)
app.register_blueprint(webpush.app, url_prefix='/webpush')


@app.route('/', defaults={'path': 'index.html'}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def staticHost(path: str):
    if request.path[-1]=='/':
        try:
            return send_file(app.static_folder+request.path+'index.html')
        except Exception:
            abort(404)
    try:
        return send_file(app.static_folder+request.path)
    except Exception:
        # Maybe 'request.path' is a directory?
        newUrl = request.base_url+'/'
        # request.base_url : http://xxx/abc
        # request.url      : http://xxx/abc?a=123
        if len(request.base_url) < len(request.url):
            newUrl += request.url[len(request.base_url):]
        return redirect(newUrl)

if __name__ == '__main__':
    app.debug = True
    if app.debug:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run()
    
