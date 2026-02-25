"""
Models for hiremind_db app
"""
from django.db import models


class HireMindUser(models.Model):
    """User model - mirrors the FastAPI auth users table"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        managed = False  # Don't manage this table with Django migrations

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Admin:
        list_display = ['email', 'name', 'created_at']
        search_fields = ['email', 'name']
        readonly_fields = ['created_at']


class ATSScore(models.Model):
    """ATS Score model"""
    user_id = models.IntegerField()
    score = models.IntegerField()
    resume_text = models.TextField(null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ats_scores'
        managed = False  # Don't manage this table with Django migrations

    def __str__(self):
        return f"ATS Score: {self.score} (User ID: {self.user_id})"

    class Admin:
        list_display = ['user_id', 'score', 'created_at']
        search_fields = ['user_id']
        ordering = ['-created_at']


class InterviewSession(models.Model):
    """Interview Session model"""
    user_id = models.IntegerField()
    question_count = models.IntegerField(null=True, blank=True)
    average_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'interview_sessions'
        managed = False  # Don't manage this table with Django migrations

    def __str__(self):
        return f"Interview Session (User ID: {self.user_id}, Avg Score: {self.average_score})"

    class Admin:
        list_display = ['user_id', 'question_count', 'average_score', 'created_at']
        search_fields = ['user_id']
        ordering = ['-created_at']
