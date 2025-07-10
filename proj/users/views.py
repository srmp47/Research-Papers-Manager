from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from Database.mongoDB import is_there_user_with_username, get_users_collection

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

    if not validate_username(username):
        return JsonResponse({"error": "Invalid username"}, status=400)
    if not validate_email(email):
        return JsonResponse({"error": "Invalid email"}, status=400)
    if not validate_name(name):
        return JsonResponse({"error": "Invalid name"}, status=400)
    if not validate_department(department):
        return JsonResponse({"error": "Invalid department"}, status=400)



     # TODO implement password validation If needed

    # TODO: remove this if needed
    #if not all([username, name, email, password, department]):
    #    return JsonResponse({"error": "All fields are required"}, status=400)

    if is_there_user_with_username(username):
        return JsonResponse({"error": "Username already taken"}, status=409)

    users_col = get_users_collection()
    user_doc = {
        "username": username,
        "name": name,
        "email": email,
        "password": password,  # Note: should hash in production
        "department": department
    }
    result = users_col.insert_one(user_doc)
    return JsonResponse({"message": "User registered", "user_id": str(result.inserted_id)}, status=201)
