import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Database.mongoDB import get_users_collection, get_papers_collection, is_there_user_with_id , is_there_paper_with_paper_id , get_citations_collection
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
    for paper_id in citations:
        try:
            paper_id_object = ObjectId(paper_id)
            if not is_there_paper_with_paper_id(paper_id_object):
                return False
        except:
            return False
    return True


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
    if not is_there_user_with_id(user_obj_id):
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
    if citations is not None and  not validate_citations(citations):
        return JsonResponse({"error": f"Invalid citations: {citations}"}, status=400)

    papers_col = get_papers_collection()
    citations_col = get_citations_collection()
    for cited_id in citations:
        try:
            cited_obj_id = ObjectId(cited_id)
        except Exception:
            return JsonResponse({"error": f"Invalid citation ID format: {cited_id}"}, status=404)
        if not papers_col.find_one({"_id": cited_obj_id}):
            return JsonResponse({"error": f"Citation not found: {cited_id}"}, status=404)
    
    paper_doc = {
        "title": title,
        "authors": authors ,
        "abstract": abstract,
        "publication_date": publication_date,
        "journal_conference": journal_conference,
        "keywords": keywords,
        "citations": citations,
        "uploaded_by": user_id,
        "views": 0
    }
    result = papers_col.insert_one(paper_doc)
    for cited_id in citations:
        cited_id = ObjectId(cited_id)
        paper_id = ObjectId(result.inserted_id)
        citation_doc = {
            "paper_id" : paper_id ,
            "cited_paper_id" : cited_id
        }
        citations_col.insert_one(citation_doc)


    return JsonResponse({"message": "Paper uploaded", "paper_id": str(result.inserted_id)}, status=201)


@csrf_exempt
def get_papers(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    papers_col = get_papers_collection()
    search = request.GET.get("search")
    sort_by = request.GET.get("sorted_by")
    order = request.GET.get("order")
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"abstract": {"$regex": search, "$options": "i"}}
        ]
    if sort_by is not None and sort_by not in ["publication_date", "relevance"]:
        return JsonResponse({"error": "Invalid value for sort_by"}, status=400)

    if order is not None and order not in ["asc", "desc"]:
        return JsonResponse({"error": "Invalid value for order"}, status=400)
    sort_direction = 1 if order == "asc" else -1
    sort_field = "views" if sort_by == "relevance" else "publication_date"

    papers_cursor = papers_col.find(query).sort(sort_field, sort_direction)
    papers_list = []
    for paper in papers_cursor:
        citation_count = len(paper.get("citations"))

        papers_list.append({
            "id": str(paper["_id"]),
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "abstract": paper.get("abstract", ""),
            "publication_date": paper.get("publication_date", ""),
            "journal_conference": paper.get("journal_conference", ""),
            "keywords": paper.get("keywords", []),
            "citation_count": citation_count,
            "views": paper.get("views", 0)
        })

    return JsonResponse({"papers": papers_list}, status=200)


@csrf_exempt
def get_paper_details(request, paper_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    papers_col = get_papers_collection()

    try:
        paper_obj_id = ObjectId(paper_id)
    except Exception:
        return JsonResponse({"error": "Invalid paper ID format"}, status=404)

    paper = papers_col.find_one({"_id": paper_obj_id})
    if not paper:
        return JsonResponse({"error": "Paper not found"}, status=404)

    citation_count = len(paper.get("citations", []))

    response_data = {
        "id": str(paper["_id"]),
        "title": paper.get("title", ""),
        "authors": paper.get("authors", []),
        "abstract": paper.get("abstract", ""),
        "publication_date": paper.get("publication_date", ""),
        "journal_conference": paper.get("journal_conference", ""),
        "keywords": paper.get("keywords", []),
        "citation_count": citation_count,
        "views": paper.get("views", 0)
    }

    return JsonResponse(response_data, status=200)


