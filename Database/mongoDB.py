import json

from asgiref.timeout import timeout
from bson import ObjectId
from pymongo import MongoClient
import redis
import bcrypt

_mongo_client = None
# mongoDB :
def get_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(
            "mongodb://localhost:27017",
            maxPoolSize=50,
            connectTimeoutMS=30000,
            serverSelectionTimeoutMS=30000
        )
    return _mongo_client["mongoDB"]

def get_users_collection():
    return get_db()["Users"]

#def is_there_user_with_username(username):
#    users_col = get_users_collection()
#    return users_col.find_one({"username": username}) is not None

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



# Redis :

_redis_pool = None

def get_redis():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(host="localhost", port=6380, db=0)
    return redis.Redis(connection_pool=_redis_pool)

def is_there_username(username):
    result = get_redis().hexists("usernames",username)
    return result


def register_user(username):
    get_redis().hset("usernames",username, '1')

def save_search_result(search_arguments,search_result):
    get_redis().setex(f"search:{search_arguments}",500, json.dumps(search_result))

def is_there_search_result(search_arguments):
    return get_redis().exists(f"search:{search_arguments}")

def get_search_result(search_arguments):
    return json.loads( get_redis().get(f"search:{search_arguments}"))

def get_views_of_paper(paper_id):
    views = get_redis().get(f"paper_views:{paper_id}")
    if views is None:
        return 0
    return int(views.decode())

def increase_views_of_paper(paper_id):
    get_redis().incr(f"paper_views:{paper_id}")


def transfer_views_to_mongodb():
    redis = get_redis()
    keys = redis.keys("paper_views:*")
    papers_col = get_papers_collection()

    for key in keys:
        paper_id = key.decode().split(':')[1]
        redis_count = get_views_of_paper(paper_id)
        if redis_count > 0:
            papers_col.update_one(
                {'_id': ObjectId(paper_id)},
                {'$inc': {'views': redis_count}}
            )
        redis.set(key , 0)


