**Deployed at https://enjoin-2.herokuapp.com**

> 錢多大魯再加蛋，孤單寂寞沒人伴，Enjoin 讓你找到伴 – 家浩, 羿婷, 同益, 雅心, 秉諭, 志健, 哲銓

Restful API, Python 3.7

## Setup
```
pip install -r requirements.txt
```
And a /key.json file is needed to connect to a mongo db server.

E.g.

```
{
    "db": "@123.123.mongodb.net/myDatabase?retryWrites=true&w=majority",
    "user": "xxx",
    "password": "123"
}
```

## Run
```
python app.py
```

### Structure 
<pre>
/app.py   
/models.py   
/routes/  
   /__init__.py  
   /account.py  
   /menu.py  
   /Order.py
</pre>

### Tool for Testing API

* [Postman](https://www.getpostman.com/downloads/)
