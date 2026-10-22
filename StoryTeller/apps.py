from django.apps import AppConfig


class StorytellerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'StoryTeller'

    def ready(self):
        from . import compat

        compat.apply()
