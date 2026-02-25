"""
Admin configuration for hiremind_db app
"""
from django.contrib import admin
from .models import HireMindUser, ATSScore, InterviewSession


@admin.register(HireMindUser)
class HireMindUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['created_at', 'id']
    ordering = ['-created_at']

    fieldsets = (
        ('User Information', {
            'fields': ('id', 'email', 'name')
        }),
        ('Security', {
            'fields': ('password_hash',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ATSScore)
class ATSScoreAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'score', 'created_at']
    search_fields = ['user_id']
    readonly_fields = ['created_at', 'id']
    ordering = ['-created_at']
    list_filter = ['score', 'created_at']

    fieldsets = (
        ('Score Information', {
            'fields': ('id', 'user_id', 'score')
        }),
        ('Details', {
            'fields': ('resume_text', 'job_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'question_count', 'average_score', 'created_at']
    search_fields = ['user_id']
    readonly_fields = ['created_at', 'id']
    ordering = ['-created_at']
    list_filter = ['average_score', 'created_at']

    fieldsets = (
        ('Session Information', {
            'fields': ('id', 'user_id')
        }),
        ('Results', {
            'fields': ('question_count', 'average_score')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
