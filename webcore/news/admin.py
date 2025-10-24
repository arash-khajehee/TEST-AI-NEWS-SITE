from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Article, Category, Tag, Comment, Newsletter, 
    ContactMessage, UserProfile, Analytics
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'article_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {};">●</span> {}',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def article_count(self, obj):
        count = obj.articles.count()
        url = reverse('admin:news_article_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} articles</a>', url, count)
    article_count.short_description = 'Articles'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'article_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        count = obj.articles.count()
        url = reverse('admin:news_article_changelist') + f'?tags__id__exact={obj.id}'
        return format_html('<a href="{}">{} articles</a>', url, count)
    article_count.short_description = 'Articles'


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['author', 'content', 'is_approved', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'status', 'featured', 
        'view_count', 'published_at', 'created_at'
    ]
    list_filter = [
        'status', 'featured', 'category', 'is_published', 
        'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'author__username', 'author__first_name', 'author__last_name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['view_count', 'share_count', 'reading_time', 'created_at', 'updated_at']
    inlines = [CommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'author', 'category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt'),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': ('status', 'featured', 'is_published', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('view_count', 'share_count', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')
    
    def save_model(self, request, obj, form, change):
        if not change:  # New article
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'article', 'author', 'content_preview', 'is_approved', 
        'is_highlighted', 'created_at'
    ]
    list_filter = ['is_approved', 'is_highlighted', 'created_at', 'article__category']
    search_fields = ['content', 'author__username', 'article__title']
    list_editable = ['is_approved', 'is_highlighted']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('article', 'author', 'parent', 'content')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_highlighted', 'is_moderated', 'moderated_by', 'moderated_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'author')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'frequency', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'frequency', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    filter_horizontal = ['categories']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'get_full_name', 'location', 'newsletter_subscription', 
        'email_notifications', 'created_at'
    ]
    list_filter = ['newsletter_subscription', 'email_notifications', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'location']
    list_editable = ['newsletter_subscription', 'email_notifications']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'avatar', 'website', 'location', 'birth_date')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription', 'email_notifications')
        }),
        ('Social Media', {
            'fields': ('twitter_handle', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['article', 'date', 'views', 'shares', 'comments']
    list_filter = ['date', 'article__category']
    search_fields = ['article__title']
    readonly_fields = ['date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article')


# Customize admin site
admin.site.site_header = "News Website Administration"
admin.site.site_title = "News Admin"
admin.site.index_title = "Welcome to News Website Administration"