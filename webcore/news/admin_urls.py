from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    # Dashboard
    path('', admin_views.admin_dashboard, name='dashboard'),
    
    # Article Management
    path('articles/', admin_views.admin_articles, name='articles'),
    path('articles/create/', admin_views.admin_article_create, name='article_create'),
    path('articles/<int:article_id>/edit/', admin_views.admin_article_edit, name='article_edit'),
    path('articles/<int:article_id>/delete/', admin_views.admin_article_delete, name='article_delete'),
    
    # Comment Management
    path('comments/', admin_views.admin_comments, name='comments'),
    path('comments/<int:comment_id>/approve/', admin_views.admin_comment_approve, name='comment_approve'),
    path('comments/<int:comment_id>/reject/', admin_views.admin_comment_reject, name='comment_reject'),
    path('comments/<int:comment_id>/delete/', admin_views.admin_comment_delete, name='comment_delete'),
    
    # User Management
    path('users/', admin_views.admin_users, name='users'),
    
    # Contact Management
    path('contacts/', admin_views.admin_contacts, name='contacts'),
    path('contacts/<int:contact_id>/mark-read/', admin_views.admin_contact_mark_read, name='contact_mark_read'),
    
    # Analytics
    path('analytics/', admin_views.admin_analytics, name='analytics'),
    
    # Bulk Actions
    path('bulk-actions/', admin_views.admin_bulk_actions, name='bulk_actions'),
]



