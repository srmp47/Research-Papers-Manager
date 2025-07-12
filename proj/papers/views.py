import json
from os import MFD_ALLOW_SEALING

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Database.mongoDB import get_users_collection, get_papers_collection, is_there_user_with_username
from bson import ObjectId
from datetime import datetime


def validate_title(title):
    if not isinstance(title, str) or not title or len(title) > 200:
        return False
    return True

def validate_authors(authors):
    if (not isinstance(authors, list) or
        not all(isinstance(a, str) for a in authors) or
        not all(len(a) <= 100 for a in authors) or
        len(authors) > 5 or
        not authors):
        return False
    return True


def validate_abstract(abstract):
    if not isinstance(abstract, str) or not abstract or len(abstract) > 1000:
        return False
    return True

def validate_publication_date(publication_date):
    if not isinstance(publication_date, str) or not publication_date or not datetime.fromisoformat(publication_date):
        return False
    return True

def validate_journal_conference(journal_conference):
    if not isinstance(journal_conference, str) or not journal_conference or len(journal_conference) > 200:
        return False
    return True

def validate_keywords(keywords):
    if (not isinstance(keywords, list) or
        not all(isinstance(a, str) for a in keywords) or
        not all(len(a) <= 50 for a in keywords) or
        len(keywords) > 5 or
        not keywords):
        return False
    return True





def validate_citations(citations):
    pass


@csrf_exempt
def upload_paper(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return JsonResponse({"error": "Missing X-User-ID header"}, status=401)

    users_col = get_users_collection()
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        return JsonResponse({"error": "Invalid user ID format"}, status=401)
    if not is_there_user_with_username(user_id):
        return JsonResponse({"error": "Invalid user ID"}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    title = data.get("title")
    authors = data.get("authors")
    abstract = data.get("abstract")
    publication_date = data.get("publication_date")
    journal_conference = data.get("journal_conference")
    keywords = data.get("keywords")
    citations = data.get("citations", [])


    if title is None or abstract is None:
        return JsonResponse({"error": "title and abstract are required"}, status=400)

    if title is not None and not validate_title(title):
        return JsonResponse({"error": "Invalid or missing title"}, status=400)
    if authors is not None and not validate_authors(authors):
        return JsonResponse({"error": "Invalid or missing authors"}, status=400)
    if abstract is not None and not validate_abstract(abstract):
        return JsonResponse({"error": "Invalid or missing abstract"}, status=400)
    if publication_date is not None and not validate_publication_date(publication_date):
        return JsonResponse({"error": "Invalid or missing publication_date"}, status=400)
    if journal_conference is not None and not validate_journal_conference(journal_conference):
        return JsonResponse({"error": "Invalid or missing journal_conference"}, status=400)
    if keywords is not None and not validate_keywords(keywords):
        return JsonResponse({"error": "Invalid or missing keywords"}, status=400)
   # TODO handle this:
   # if citations is not None and not validate_citations(citations):
   #     return JsonResponse({"error": "Invalid citations"}, status=400)

    papers_col = get_papers_collection()
    for cited_id in citations:
        try:
            cited_obj_id = ObjectId(cited_id)
        except Exception:
            return JsonResponse({"error": f"Invalid citation ID format: {cited_id}"}, status=404)
        if not papers_col.find_one({"_id": cited_obj_id}):
            return JsonResponse({"error": f"Citation not found: {cited_id}"}, status=404)
    
    paper_doc = {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "publication_date": publication_date,
        "journal_conference": journal_conference,
        "keywords": keywords,
        "citations": citations,
        "uploaded_by": user_id,
        "views": 0
    }
    result = papers_col.insert_one(paper_doc)
    return JsonResponse({"message": "Paper uploaded", "paper_id": str(result.inserted_id)}, status=201)
