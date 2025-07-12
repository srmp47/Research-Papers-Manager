from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from Database.mongoDB import get_users_collection
        users_col = get_users_collection()
        users_col.create_index("username", unique=True)
