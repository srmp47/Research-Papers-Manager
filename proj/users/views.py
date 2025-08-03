from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import bcrypt

import json
from django.http import JsonResponse
from Database.mongoDB import is_there_username, get_users_collection ,register_user , get_user_with_username

import re

def validate_username(username):
    return isinstance(username, str) and bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", username))


def validate_email(email):
    if not isinstance(email, str) or len(email) > 100:
        return False
    # Simple email regex (not perfect, but covers most cases)
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email))

def validate_name(name):
    return isinstance(name, str) and len(name) <= 100

def validate_department(department):
    return isinstance(department, str) and len(department) <= 100



@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    department = data.get("department")

    if username is None or password is None or name is None:
        return JsonResponse({"error": "Username and password and Name are required"}, status=400)

    if username is not None and not validate_username(username):
        return JsonResponse({"error": "Invalid username"}, status=400)
    if email is not None and not validate_email(email):
        return JsonResponse({"error": "Invalid email"}, status=400)
    if name is not None and not validate_name(name):
        return JsonResponse({"error": "Invalid name"}, status=400)
    if department is not None and not validate_department(department):
        return JsonResponse({"error": "Invalid department"}, status=400)

    # TODO implement password validation If needed

    if username is not None and is_there_username(username):
        return JsonResponse({"error": "Username already taken"}, status=409)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt).decode()

    users_col = get_users_collection()
    user_doc = {}
    if username is not None:
        user_doc["username"] = username
    if name is not None:
        user_doc["name"] = name
    if email is not None:
        user_doc["email"] = email
    if password is not None:
        user_doc["password"] = hashed
    if department is not None:
        user_doc["department"] = department

    register_user(username)
    result = users_col.insert_one(user_doc)
    return JsonResponse({"message": "User registered", "user_id": str(result.inserted_id)}, status=201)

@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username")
    password = data.get("password")
    if username is None or password is None:
        return JsonResponse({"error": "Username and password both are required"}, status=400)

    if not is_there_username(username):
        return JsonResponse({"error": "User not found"}, status=404)

    user_doc = get_user_with_username(username)
    stored_hash = user_doc.get("password")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return JsonResponse({"error": "Incorrect password"}, status=401)

    return JsonResponse({"message": "Login successful"}, status=200)
    
