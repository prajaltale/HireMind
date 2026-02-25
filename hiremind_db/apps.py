"""
Apps configuration for hiremind_db
"""
from django.apps import AppConfig


class HiremindDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hiremind_db'
    verbose_name = 'HireMind Database'
