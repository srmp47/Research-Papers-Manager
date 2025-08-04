# seed_data.py
import os
import sys
import django
import bcrypt
import random
import pymongo
from datetime import datetime, timedelta
from faker import Faker

# Add project to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'proj')))

# Initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now import your MongoDB module
from Database.mongoDB import get_papers_collection, get_users_collection, get_citations_collection,register_user , get_redis


def create_data():
    fake = Faker()
    users_collection = get_users_collection()
    papers_collection = get_papers_collection()
    citations_collection = get_citations_collection()
    get_redis().flushall()

    # Clear existing data
    users_collection.delete_many({})
    papers_collection.delete_many({})
    citations_collection.delete_many({})
    print("Cleared existing data")

    # Create 100 users
    users = []
    for i in range(100):
        # Generate random password (8-12 characters)
        password_length = random.randint(8, 12)
        plain_password = fake.password(
            length=password_length,
            special_chars=False,
            digits=True,
            upper_case=True,
            lower_case=True
        )

        # Hash password with bcrypt
        hashed_password = bcrypt.hashpw(
            plain_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        username = fake.unique.user_name()[:20]
        users.append({
            "username": username,  # Max 20 characters
            "name": fake.name()[:100],
            "email": fake.unique.email()[:100],
            "password": hashed_password,
            "department": fake.job()[:100],
        })
        register_user(username)

    # Insert users and get their IDs
    user_result = users_collection.insert_many(users)
    user_ids = user_result.inserted_ids
    print(f"Inserted {len(user_ids)} users")

    # Create 100 papers
    papers = []
    start_date = datetime(2015, 6, 5)
    end_date = datetime(2025, 6, 5)

    for i in range(1000):
        # Generate random publication date between 2015-06-05 and 2025-06-05
        time_between = end_date - start_date
        random_days = random.randint(0, time_between.days)
        publication_date = start_date + timedelta(days=random_days)

        papers.append({
            "title": fake.sentence(nb_words=random.randint(6, 10))[:200],
            "authors": [fake.name()[:100] for _ in range(random.randint(1, 5))],
            "abstract": fake.text(max_nb_chars=1000)[:1000],
            "publication_date": publication_date,
            "journal_conference": fake.company()[:200],
            "keywords": [fake.word()[:50] for _ in range(random.randint(1, 5))],
            "uploaded_by": random.choice(user_ids),
            "views": 0,
            "citations": []  # Initialize empty citations list
        })

    # Insert papers and get their IDs
    paper_result = papers_collection.insert_many(papers)
    paper_ids = paper_result.inserted_ids
    print(f"Inserted {len(paper_ids)} papers")

    # Create citations (0-5 citations per paper, no self-citations)
    all_citations = []

    for paper_id in paper_ids:
        # Determine how many citations this paper will have (0-5)
        num_citations = random.randint(0, 5)

        # Get candidate papers (all papers except current one)
        candidate_papers = [pid for pid in paper_ids if pid != paper_id]

        # If there are not enough candidate papers, adjust the number
        if len(candidate_papers) < num_citations:
            num_citations = len(candidate_papers)

        # Randomly select papers to cite
        cited_papers = random.sample(candidate_papers, num_citations) if candidate_papers else []

        # Update the paper document with citations
        papers_collection.update_one(
            {"_id": paper_id},
            {"$set": {"citations": cited_papers}}
        )

        # Create citation documents
        for cited_paper_id in cited_papers:
            all_citations.append({
                "paper_id": paper_id,
                "cited_paper_id": cited_paper_id
            })

    # Insert citations
    if all_citations:
        citations_collection.insert_many(all_citations)
    print(f"Inserted {len(all_citations)} citations")

    print("Successfully seeded database")


if __name__ == "__main__":
    create_data()