from flask import jsonify, request, Response
from . import routes, db
import json
from bson.objectid import ObjectId
from bson import json_util
import datetime
# {    # account
#     id: 工號(int) # primary key, not null
#     password: (string) # not null
#     FAB: FAB2(選單) # not null
#     ownList: []
#     joinList: [1,2,3]
# }

# 列出IN_PROGRESS且未過期所有跟團單子
@routes.route("/Order/ListAllInProgressGroupOrder", methods=['GET'])
def ListAllInProgressGroupOrder():
    print("ListAllGroupOrder is doing something")
    order_list=list(db["order"].find({"status":"IN_PROGRESS"}))
    still_alive_order = []
    for order in order_list:
        current_time = datetime.datetime.now()
        order_end_time = datetime.datetime.strptime(order["meet_time"][1], "%Y-%m-%dT%H:%M")
        
        if  current_time - order_end_time < datetime.timedelta(minutes=1):
            still_alive_order.append(order)

    if len(still_alive_order) ==0:
        return jsonify(message="No IN_PROGRESS Order")
    else:
        for order in still_alive_order:
            order['_id'] = str(order['_id'])
        return Response(json.dumps(still_alive_order), mimetype="application/json")

# 列出COMPLETED所有跟團單子
@routes.route("/Order/ListAllCompletedGroupOrder", methods=['GET'])
def ListAllCompletedGroupOrder():
    print("ListAllGroupOrder is doing something")
    order_list=list(db["order"].find({"status":"COMPLETED"}))
    if len(order_list) ==0:
        return jsonify(message="No COMPLETED Order")
    else:
        for order in order_list:
            order['_id'] = str(order['_id'])
        return Response(json.dumps(order_list), mimetype="application/json")

# 列出CLOSED所有跟團單子
@routes.route("/Order/ListAllClosedGroupOrder", methods=['GET'])
def ListAllClosedGroupOrder():
    print("ListAllGroupOrder is doing something")
    order_list=list(db["order"].find({"status":"CLOSED"}))
    if len(order_list) ==0:
        return jsonify(message="No CLOSED Order")
    else:
        for order in order_list:
            order['_id'] = str(order['_id'])
        return Response(json.dumps(order_list), mimetype="application/json")

# 搜尋hashtag
@routes.route("/Order/SearchByHashtag", methods=['POST'])
def SearchByHashtag():
    order_table = db['order']
    # list of hashtags
    search_key = request.get_json()['search_key'].split()

    query=[]
    for s_k in search_key:
        for field in ['title', 'comment', 'hashtag', 'store', 'drink', 'creator_id', 'meet_factory', 'meet_time']:
            query.append({field: {"$regex": s_k, '$options': 'i'}})
    result = list(db["order"].find({'$or': query}))
    return jsonify(result)



@routes.route("/Order/JoinOrder/<string:uuid>/<string:goid>", methods=["POST"])
def JoinOrder(uuid, goid):
    print("uuid",uuid)
    print("goid", goid)
    order_result = db["order"].find_one({'_id': ObjectId(goid)})
    if order_result["join_people"]==order_result["join_people_bound"]:
        print("The number is full")
        return jsonify(message="The number is full")
    ## Update account joinOrder, add order id into joinOrder
    account_result = db["account"].find_one({'_id': ObjectId(uuid)})
    join_id_list = [account_result["id"]]
    join_order_list = [ObjectId(goid)]
    if "joinOrder" in account_result:
        if account_result["joinOrder"]:
            if ObjectId(goid) in account_result["joinOrder"]:
                return jsonify(message="you are already in this order")
            join_order_list += account_result["joinOrder"]
    db['account'].update_one({'_id': ObjectId(uuid)}, {"$set": {"joinOrder": join_order_list}})

    ## Update Order join people
    # {
    # "meet_time" : ["2021-07-29T10:00:00.000Z", "2021-07-29T10:10:00.000Z"],
    # "meet_factory" : "FAB18",
    # "store" : "Louisa",
    # "drink" : "特濃小卡布",
    # "hashtag" : ["FAB18", "Louisa", "特濃小卡布"],
    # "title" : "特濃小卡布買四送二",
    # "comment" : "KKKKK",
    # "status" : "IN_PROGRESS",
    # "creator_id" : "1745",
    # "join_people" : "2"
    # "join_people_account": []
    # }
    order_result = db["order"].find_one({'_id': ObjectId(goid)})
    join_people = order_result["join_people"]+1
    if "join_people_id" in order_result:
        join_id_list += order_result["join_people_id"]
    if join_people == order_result["join_people_bound"]:
        db["order"].update_one({'_id': ObjectId(goid)}, {"$set": {"join_people": join_people, "status":"COMPLETED", "join_people_id":join_id_list}})
    else:
        db["order"].update_one({'_id': ObjectId(goid)}, {"$set": {"join_people": join_people, "join_people_id":join_id_list}})
    # db['account'].insert_one({'id': _id, 'password': password, 'fab': fab})
    return jsonify(message="success")

@routes.route("/Order/QuitOrder/<string:uuid>/<string:goid>", methods=["POST"])
def QuitOrder(uuid, goid):
    ## uuid is ObjectId(account _id)
    ## goid is ObjectId(order _id)
    
    order_result = db["order"].find_one({'_id': ObjectId(goid)})
    if order_result["status"]=="CLOSED":
        ## Return old account collections and order collections
        orders = db["order"].find()
        order_lst = []
        for order in orders:
            order["_id"] = str(order["_id"])
            order_lst.append(order)
        accounts = db["account"].find()
        account_lst = []
        for account in accounts:
            account["_id"] = str(account["_id"])
            if account.get("joinOrder")!=None:
                for i in range (len(account["joinOrder"])):
                    account["joinOrder"][i] = str(account["joinOrder"][i])
            if account.get("ownOrder") !=None:
                for i in range (len(account["ownOrder"])):
                    account["ownOrder"][i] = str(account["ownOrder"][i])
            account_lst.append(account)
        return Response(json.dumps(order_lst), json.dumps(account_lst), mimetype="application/json")
        #return jsonify(message = "This order is already closed, you couldn't quit", order=order_lst, account=account_lst)
    
    ## Find account and remove order from join order
    account_result = db["account"].find_one({'_id': ObjectId(uuid)})
    if ObjectId(goid) in account_result["joinOrder"]:
        account_result["joinOrder"].remove(ObjectId(goid))
        db['account'].update_one({'_id': ObjectId(uuid)}, {"$set": {"joinOrder": account_result["joinOrder"]}})
        ## Remove join account from order
        order_result["join_people_id"].remove(account_result["id"])
        join_people = order_result["join_people"]-1
        db["order"].update_one({'_id': ObjectId(goid)}, {"$set": {"join_people": join_people, "join_people_id":order_result["join_people_id"], "status":"IN_PROGRESS"}})
    ## Return new account collections and order collections
    orders = db["order"].find()
    order_lst = []
    for order in orders:
        order["_id"] = str(order["_id"])
        order_lst.append(order)
    accounts = db["account"].find()
    account_lst = []
    for account in accounts:
        account["_id"] = str(account["_id"])
        if account.get("joinOrder")!=None:
            for i in range (len(account["joinOrder"])):
                account["joinOrder"][i] = str(account["joinOrder"][i])
        if account.get("ownOrder") !=None:
            for i in range (len(account["ownOrder"])):
                account["ownOrder"][i] = str(account["ownOrder"][i])

        #account["joinOrder"] = str(account["joinOrder"])
        account_lst.append(account)
    #return Response(json.dumps(order_lst), mimetype="application/json")
    return jsonify(message='Remove Success!', order=order_lst, account=account_lst)
