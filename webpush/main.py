import logging
import json, os

from flask import request, Response, render_template, jsonify, Flask
from pywebpush import webpush, WebPushException

# app = Flask(__name__)
# app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
from flask import Blueprint
app = Blueprint('webpush', __name__)
# app = Blueprint('webpush', __name__, template_folder=os.path.join(os.path.dirname(__file__),"templates"))

DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.path.dirname(__file__),"private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.path.dirname(__file__),"public_key.txt")

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")
# print('VAPID_PRIVATE_KEY',VAPID_PRIVATE_KEY)
# print('VAPID_PUBLIC_KEY',VAPID_PUBLIC_KEY)

VAPID_CLAIMS = {
"sub": "mailto:develop@raturi.in"
}

def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )

# @app.route('/')
# def index():
#     return render_template("/templates/"+'index.html')

@app.route("/subscription/", methods=["GET", "POST"])
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """

    if request.method == "GET":
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")

    subscription_token = request.get_json("subscription_token")
    return Response(status=201, mimetype="application/json")

from datetime import datetime
@app.route("/push_v1/",methods=['POST'])
def push_v1():
    message = "Enjoin Test at " + str(datetime.now())
    print("is_json",request.is_json)

    if not request.json or not request.json.get('sub_token'):
        return jsonify({'failed':1})

    print("request.json",request.json)

    token = request.json.get('sub_token')
    try:
        token = json.loads(token)
        print('json.loads',token)
        print('===============================')
        res=send_web_push(token, message)
        print('done send_web_push()')
        print('res:', res, res.content, ', type:', type(res))
        return jsonify({'success':1})
        # return res
    except Exception as e:
        print("error",e)
        return jsonify({'failed':str(e)})

if __name__ == "__main__":
    app.debug = True
    if app.debug:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(port=3456)
