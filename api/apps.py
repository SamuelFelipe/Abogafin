from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'


class LawyerUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lawyer_user'


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Blog'
