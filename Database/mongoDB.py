from pymongo import MongoClient

def get_db():
    client = MongoClient(
        "mongodb://reza:9358@localhost:27017/mongoDB?authSource=mongoDB"
    )
    db = client["mongoDB"]
    return db

def get_users_collection():
    return get_db()["Users"]

def is_there_user_with_username(username):
    users_col = get_users_collection()

def get_user_with_username(username):
    return get_users_collection().find_one({"username": username})


def get_papers_collection():
    return get_db()["Papers"]

def is_there_paper_with_paper_id(paper_id):
    papers_col = get_papers_collection()
    return papers_col.find_one({"paper_id": paper_id}) is not None

def get_paper_with_paper_id(paper_id):
    papers_col = get_papers_collection()
    return papers_col.find_one({"paper_id": paper_id})


