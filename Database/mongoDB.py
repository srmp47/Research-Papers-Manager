from pymongo import MongoClient

def get_db():
    client = MongoClient(
        "mongodb://localhost:27017"
    )
    db = client["mongoDB"]
    return db

def get_users_collection():
    return get_db()["Users"]

def is_there_user_with_username(username):
    users_col = get_users_collection()
    return users_col.find_one({"username": username}) is not None

def is_there_user_with_id(user_id):
    users_col = get_users_collection()
    return users_col.find_one({"_id":user_id}) is not None

def get_user_with_username(username):
    return get_users_collection().find_one({"username": username})


def get_papers_collection():
    return get_db()["Papers"]

def is_there_paper_with_paper_id(paper_id):
    papers_col = get_papers_collection()
    return papers_col.find_one({"_id": paper_id}) is not None

def get_paper_with_paper_id(paper_id):
    papers_col = get_papers_collection()
    return papers_col.find_one({"_id": paper_id})


def get_citations_collection():
    return get_db()["Citations"]

def is_there_citation_with_citation_id(citation_id):
    citations_col = get_citations_collection()
    return citations_col.find_one({"citation_id": citation_id}) is not None

def get_citation_with_citation_id(citation_id):
    citations_col = get_citations_collection()
    return citations_col.find_one({"citation_id": citation_id})

