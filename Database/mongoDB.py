from pymongo import MongoClient

def get_db():
    # اتصال با احراز هویت با کاربر جدید
    client = MongoClient(
        "mongodb://reza:9358@localhost:27017/mongoDB?authSource=mongoDB"
    )
    db = client["mongoDB"]
    return db

def get_users_collection():
    return get_db()["Users"]

def is_there_user_with_username(username):
    users_col = get_users_collection()
    return users_col.find_one({"username": username}) is not None