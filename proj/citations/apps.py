from django.apps import AppConfig


class CitationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'citations'
    def ready(self):
        from Database.mongoDB import get_citations_collection
        citations_col  = get_citations_collection()
        citations_col.create_index(
            "cited_paper_id", 1
        )
