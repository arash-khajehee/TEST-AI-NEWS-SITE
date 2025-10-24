from django.conf import settings
from .models import Category, Tag


def news_context(request):
    """Global context processor for news website"""
    context = {
        'site_name': getattr(settings, 'SITE_NAME', 'News Website'),
        'site_description': getattr(settings, 'SITE_DESCRIPTION', 'Latest news and articles'),
        'site_keywords': getattr(settings, 'SITE_KEYWORDS', 'news, articles, latest, updates'),
        'categories': Category.objects.filter(is_active=True)[:10],
        'popular_tags': Tag.objects.all()[:20],
    }
    return context



