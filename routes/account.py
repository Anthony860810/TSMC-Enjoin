from flask import jsonify, request, current_app
from . import routes, db
from bson.objectid import ObjectId
from bson import json_util
import json
import jwt
import config
from datetime import datetime, timedelta
from functools import wraps

# {    # account
#     id: 工號(int) # primary key, not null
#     password: (string) # not null
#     epidemic_prevention_group : A/B # not null
#     ownOrder: []
#     joinOrder: []
# }
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return 'Unauthorized Access!', 401
        data = jwt.decode(token, config.SECRET_KEY, algorithm="HS256")
        current_user = db['account'].find_one({'id': data['id']})
        if not current_user:
            return 'Unauthorized Access!', 401
        return f(*args, **kwargs)
    return decorated

# test
@routes.route('/Account/LoginTest', methods=['GET'])
@token_required
def test():
    print("authorized")
    return jsonify(message="Authorized, is already logged in")

# show DB values
@routes.route('/testDB', methods=['GET'])
def testDB():
    orders = db["order"].find()
    order_lst = []
    for order in orders:
        order["_id"] = str(order["_id"])
        order_lst.append(order)
    accounts = db["account"].find()
    account_lst = []
    for account in accounts:
        account["_id"] = str(account["_id"])
        account_lst.append(account)
    return jsonify(message='it works!', order=order_lst, account=account_lst)

# 註冊
@routes.route("/Account/Create", methods=['POST'])
def accountCreate():
    bcrypt = current_app.config["bcrypt"]
    req = request.get_json()
    _id = req['id']
    # 加密
    password = bcrypt.generate_password_hash(req['password']).decode("utf-8")
    group = req['epidemic_prevention_group']
    result = db['account'].find_one({'id': _id})
    if result:
        response = jsonify(message="已註冊過的工號")
    else:
        db['account'].insert_one({'id': str(_id), 'password': password, 'epidemic_prevention_group': group})
        response = jsonify(message="註冊成功")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

#  登入
@routes.route("/Account/Login", methods=['POST'])
def accountLogin():
    bcrypt = current_app.config["bcrypt"]
    req = request.get_json()
    _id = req['id']
    password = req['password']
    result = db['account'].find_one({'id': _id})
    if result: 
        if bcrypt.check_password_hash(result['password'], password):
            token = jwt.encode({
                'id': _id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, config.SECRET_KEY, algorithm="HS256")
            response = jsonify(message="成功登入", token= token.decode('UTF-8'), id= _id, _id= result["_id"])
        else:
            response = jsonify(message="登入失敗，密碼錯誤")
    else:
        response = jsonify(message="查無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response    

#  新增單子
@routes.route("/Account/CreateOrder/<string:tsmcid>", methods=['POST'])
@token_required
def createOrder(tsmcid):
    form = request.get_json()
    result = db['account'].find_one({'id': tsmcid})
    if result:
        meet_factory = form["meet_factory"]
        store = form["store"]
        drink = form["drink"]
        form['status'] = "IN_PROGRESS"
        form['hashtag'] = [meet_factory, store, drink]
        form['creator_id'] = str(tsmcid)
        form['meet_time'] = [form["meet_time_start"], form["meet_time_end"]]
        form['join_people_bound'] = int(form["join_people_bound"])
        form['join_people'] = 0
        if "epidemic_prevention_group" in result:
            form['epidemic_prevention_group'] = result["epidemic_prevention_group"]
        if "comment" not in form:
            form['comment'] = ""
        del form['meet_time_start']
        del form['meet_time_end']
        insert = db['order'].insert_one(form)
        orderUuid = insert.inserted_id 

        if 'ownOrder' in result:
            ownOrder = result["ownOrder"] + [orderUuid]
        else:
            ownOrder = [orderUuid]
        
        db["account"].update_one({'id': tsmcid}, {"$set": {'ownOrder': ownOrder}})
        response = jsonify(message="建立揪團單子成功")
    else:
        response = jsonify(message="無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response   

## 更新自己的單子(擁有者更新時間、地點、....)
@routes.route("/Account/UpdateOrder/<string:tsmcid>/<string:goid>", methods=['POST'])
@token_required
def editOrder(tsmcid, goid):
    form = request.get_json()
    account = db['account'].find_one({'id': tsmcid})
    if account:
        # 確認帳號是否有創建單子
        if "ownOrder" in account:
            # 確認單子是否為此擁有者
            if ObjectId(goid) in account["ownOrder"]:
                result = db['order'].find_one({'_id': ObjectId(goid)})
                if result:
                    meet_factory = form["meet_factory"]
                    store = form["store"]
                    drink = form["drink"]
                    result["store"] = store
                    result["drink"] = drink
                    result["meet_factory"] = meet_factory
                    result['hashtag'] = [meet_factory, store, drink]
                    result['meet_time'] = [form["meet_time_start"], form["meet_time_end"]]
                    result['join_people_bound'] = int(form["join_people_bound"])
                    result['comment'] = form["comment"]
                    result['title'] = form["title"]
                    # print(result)
                    if (result['join_people_bound'] > result['join_people']):
                        result["status"] = "IN_PROGRESS"
                        db["order"].replace_one({'_id': ObjectId(goid)}, result)
                        response = jsonify(message="編輯揪團單子成功")
                    elif (result['join_people_bound'] < result['join_people']):
                        response = jsonify(message="跟團人數大於限制人數，無法進行修正")
                    else:
                        result["status"] = "COMPLETED"
                        db["order"].replace_one({'_id': ObjectId(goid)}, result)
                        response = jsonify(message="編輯揪團單子成功")
                else:
                    response = jsonify(message="此單子已被刪除")
            else:
                response = jsonify(message="非此揪團單子的擁有者")
        else:
            response = jsonify(message="無創建的單子")
    else:
        response = jsonify(message="無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response   

## 完成單子(確認揪團成功)
@routes.route("/Account/CloseOrder/<string:tsmcid>/<string:goid>", methods=['POST'])
@token_required
def closeOrder(tsmcid, goid):
    result = db['account'].find_one({'id': tsmcid})
    if result: 
        if "ownOrder" in result:
            if ObjectId(goid) in result["ownOrder"]:
                order = db['order'].find_one({'_id': ObjectId(goid)})
                if order["status"] == "COMPLETED":
                    db["order"].update_one({'_id': ObjectId(goid)}, {"$set": {'status': "CLOSED"}})
                    response = jsonify(message="更新status成功")
                else:
                    response = jsonify(message="揪團人數尚未滿員，無法結單")
            else:
                response = jsonify(message="非此單子的擁有者")
        else:
            response = jsonify(message="無建立的單子")
    else:
        response = jsonify(message="無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response  

## 棄單(刪除單子)
@routes.route("/Account/DeleteCreatedOrder/<string:tsmcid>/<string:goid>", methods=['DELETE'])
@token_required
def deleteOrder(tsmcid, goid):
    result = db['account'].find_one({'id': tsmcid})
    if result: 
        if "ownOrder" in result:
            order = db['order'].find_one({'_id': ObjectId(goid)})
            if order:
                if ObjectId(goid) in result["ownOrder"]:
                    response = jsonify(message="刪除單子成功")
                    #移除ownOrder list
                    ownOrder = result["ownOrder"]
                    ownOrder.remove(ObjectId(goid))
                    db["account"].update_one({'id': tsmcid}, {"$set": {'ownOrder': ownOrder}})
                    #移除joinOrder list
                    if "join_people_id" in order:
                        for joinPeopleId in order["join_people_id"]:
                            res = db['account'].find_one({'id': joinPeopleId})
                            joinOrder = res["joinOrder"]
                            if ObjectId(goid) in joinOrder:
                                joinOrder.remove(ObjectId(goid))
                                db["account"].update_one({'id': tsmcid}, {"$set": {'joinOrder': joinOrder}})
                    db["order"].delete_one({'_id': ObjectId(goid)})
                    response.status_code = 200
                else:
                    response = jsonify(message="非此單子的擁有者")
            else:
                response = jsonify(message="此單子已刪除")
        else:
            response = jsonify(message="無建立的單子")
    else:
        response = jsonify(message="無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response  

## get跟團的所有單子
@routes.route("/Account/ListOwnerGroupOrder/<string:tsmcid>", methods=['GET'])
@token_required
def getJoinOrder(tsmcid):
    result = db['account'].find_one({'id': tsmcid})
    if result: 
        data = []
        if "joinOrder" in result:
            for objectid in result["joinOrder"]:
                order = db["order"].find_one({'_id': objectid})
                if order:
                    order["_id"] = str(order["_id"])
                    data.append(order)
            response = jsonify(message="success", data=data)
        else:
            response = jsonify(message="無跟團的單子")
    else:
        response = jsonify(message="無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

## get自己創的所有單子
@routes.route("/Account/ListOwnerCreatedGroupOrder/<string:tsmcid>", methods=['GET'])
@token_required
def getOwnerOrder(tsmcid):
    result = db['account'].find_one({'id': tsmcid})
    if result: 
        data = []
        if "ownOrder" in result:
            for objectid in result["ownOrder"]:
                order = db["order"].find_one({'_id': objectid})
                if order:
                    order["_id"] = str(order["_id"])
                    data.append(order)
            response = jsonify(message="success", data=data)
        else:
            response = jsonify(message="無創建的單子")
    else:
        response = jsonify(message="無此帳號")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['Access-Control-Allow-Method'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

