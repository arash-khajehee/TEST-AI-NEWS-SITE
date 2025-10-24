from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

from .models import Article, Category, Comment, UserProfile, Newsletter, ContactMessage, Analytics
from .forms import ArticleForm


def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_staff or user.is_superuser


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics and quick actions"""
    
    # Get statistics
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status='published', is_published=True).count()
    draft_articles = Article.objects.filter(status='draft').count()
    total_comments = Comment.objects.count()
    pending_comments = Comment.objects.filter(is_approved=False).count()
    total_users = User.objects.count()
    newsletter_subscribers = Newsletter.objects.filter(is_active=True).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    # Recent activity
    recent_articles = Article.objects.select_related('author', 'category').order_by('-created_at')[:5]
    recent_comments = Comment.objects.select_related('author', 'article').order_by('-created_at')[:5]
    recent_contacts = ContactMessage.objects.order_by('-created_at')[:5]
    
    # Analytics data
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Article views this week
    weekly_views = Article.objects.filter(
        published_at__date__gte=week_ago
    ).aggregate(total_views=Sum('view_count'))['total_views'] or 0
    
    # Most popular articles
    popular_articles = Article.objects.filter(
        status='published',
        is_published=True
    ).order_by('-view_count')[:5]
    
    # Category distribution
    category_stats = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    ).order_by('-article_count')
    
    # Recent analytics
    recent_analytics = Analytics.objects.select_related('article').order_by('-date')[:10]
    
    # Get additional context for sidebar
    pending_comments = Comment.objects.filter(is_approved=False).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'total_comments': total_comments,
        'pending_comments': pending_comments,
        'total_users': total_users,
        'newsletter_subscribers': newsletter_subscribers,
        'unread_contacts': unread_contacts,
        'weekly_views': weekly_views,
        'recent_articles': recent_articles,
        'recent_comments': recent_comments,
        'recent_contacts': recent_contacts,
        'popular_articles': popular_articles,
        'category_stats': category_stats,
        'recent_analytics': recent_analytics,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def admin_articles(request):
    """Custom article management interface"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Build queryset
    articles = Article.objects.select_related('author', 'category').prefetch_related('tags')
    
    if status_filter:
        articles = articles.filter(status=status_filter)
    
    if category_filter:
        articles = articles.filter(category_id=category_filter)
    
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Order by creation date
    articles = articles.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.all()
    
    # Get additional context for sidebar
    pending_comments = Comment.objects.filter(is_approved=False).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'pending_comments': pending_comments,
        'unread_contacts': unread_contacts,
    }
    
    return render(request, 'admin/articles.html', context)


@staff_member_required
def admin_article_create(request):
    """Create new article from admin panel"""
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, f'Article "{article.title}" created successfully!')
            return redirect('news:admin_articles')
    else:
        form = ArticleForm()
    
    return render(request, 'admin/article_form.html', {
        'form': form,
        'title': 'Create New Article',
        'action': 'Create'
    })


@staff_member_required
def admin_article_edit(request, article_id):
    """Edit article from admin panel"""
    
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f'Article "{article.title}" updated successfully!')
            return redirect('news:admin_articles')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'admin/article_form.html', {
        'form': form,
        'article': article,
        'title': f'Edit Article: {article.title}',
        'action': 'Update'
    })


@staff_member_required
def admin_article_delete(request, article_id):
    """Delete article from admin panel"""
    
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        article_title = article.title
        article.delete()
        messages.success(request, f'Article "{article_title}" deleted successfully!')
        return redirect('news:admin_articles')
    
    return render(request, 'admin/article_confirm_delete.html', {
        'article': article
    })


@staff_member_required
def admin_comments(request):
    """Comment management interface"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Build queryset
    comments = Comment.objects.select_related('author', 'article').order_by('-created_at')
    
    if status_filter == 'approved':
        comments = comments.filter(is_approved=True)
    elif status_filter == 'pending':
        comments = comments.filter(is_approved=False)
    
    if search_query:
        comments = comments.filter(
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(article__title__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(comments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get additional context for sidebar
    pending_comments = Comment.objects.filter(is_approved=False).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'pending_comments': pending_comments,
        'unread_contacts': unread_contacts,
    }
    
    return render(request, 'admin/comments.html', context)


@staff_member_required
def admin_comment_approve(request, comment_id):
    """Approve comment"""
    
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.is_moderated = True
    comment.moderated_by = request.user
    comment.moderated_at = timezone.now()
    comment.save()
    
    messages.success(request, 'Comment approved successfully!')
    return redirect('news:admin_comments')


@staff_member_required
def admin_comment_reject(request, comment_id):
    """Reject comment"""
    
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = False
    comment.is_moderated = True
    comment.moderated_by = request.user
    comment.moderated_at = timezone.now()
    comment.save()
    
    messages.success(request, 'Comment rejected successfully!')
    return redirect('news:admin_comments')


@staff_member_required
def admin_comment_delete(request, comment_id):
    """Delete comment"""
    
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('news:admin_comments')
    
    return render(request, 'admin/comment_confirm_delete.html', {
        'comment': comment
    })


@staff_member_required
def admin_users(request):
    """User management interface"""
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    user_type = request.GET.get('type', '')
    
    # Build queryset
    users = User.objects.select_related('profile').order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if user_type == 'staff':
        users = users.filter(is_staff=True)
    elif user_type == 'superuser':
        users = users.filter(is_superuser=True)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get additional context for sidebar
    pending_comments = Comment.objects.filter(is_approved=False).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type': user_type,
        'pending_comments': pending_comments,
        'unread_contacts': unread_contacts,
    }
    
    return render(request, 'admin/users.html', context)


@staff_member_required
def admin_contacts(request):
    """Contact message management"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Build queryset
    contacts = ContactMessage.objects.order_by('-created_at')
    
    if status_filter == 'read':
        contacts = contacts.filter(is_read=True)
    elif status_filter == 'unread':
        contacts = contacts.filter(is_read=False)
    
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get additional context for sidebar
    pending_comments = Comment.objects.filter(is_approved=False).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'pending_comments': pending_comments,
        'unread_contacts': unread_contacts,
    }
    
    return render(request, 'admin/contacts.html', context)


@staff_member_required
def admin_contact_mark_read(request, contact_id):
    """Mark contact message as read"""
    
    contact = get_object_or_404(ContactMessage, id=contact_id)
    contact.is_read = True
    contact.save()
    
    messages.success(request, 'Contact message marked as read!')
    return redirect('news:admin_contacts')


@staff_member_required
def admin_analytics(request):
    """Analytics dashboard"""
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Article performance
    articles = Article.objects.filter(
        status='published',
        is_published=True,
        published_at__date__gte=start_date
    ).order_by('-view_count')
    
    # Daily views for the last 30 days
    daily_views = []
    for i in range(30):
        date = end_date - timedelta(days=i)
        views = Article.objects.filter(
            published_at__date=date,
            status='published'
        ).aggregate(total_views=Sum('view_count'))['total_views'] or 0
        daily_views.append({
            'date': date,
            'views': views
        })
    
    # Category performance
    category_performance = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published')),
        total_views=Sum('articles__view_count', filter=Q(articles__status='published'))
    ).order_by('-total_views')
    
    # Get additional context for sidebar
    pending_comments = Comment.objects.filter(is_approved=False).count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'articles': articles[:10],
        'daily_views': daily_views,
        'category_performance': category_performance,
        'start_date': start_date,
        'end_date': end_date,
        'pending_comments': pending_comments,
        'unread_contacts': unread_contacts,
    }
    
    return render(request, 'admin/analytics.html', context)


@staff_member_required
def admin_bulk_actions(request):
    """Bulk actions for content management"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_items = request.POST.getlist('selected_items')
        
        if action == 'publish_articles':
            Article.objects.filter(id__in=selected_items).update(
                status='published',
                is_published=True,
                published_at=timezone.now()
            )
            messages.success(request, f'{len(selected_items)} articles published!')
        
        elif action == 'unpublish_articles':
            Article.objects.filter(id__in=selected_items).update(
                is_published=False
            )
            messages.success(request, f'{len(selected_items)} articles unpublished!')
        
        elif action == 'approve_comments':
            Comment.objects.filter(id__in=selected_items).update(
                is_approved=True,
                is_moderated=True,
                moderated_by=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(selected_items)} comments approved!')
        
        elif action == 'delete_comments':
            Comment.objects.filter(id__in=selected_items).delete()
            messages.success(request, f'{len(selected_items)} comments deleted!')
        
        elif action == 'mark_contacts_read':
            ContactMessage.objects.filter(id__in=selected_items).update(is_read=True)
            messages.success(request, f'{len(selected_items)} contact messages marked as read!')
        
        return redirect(request.META.get('HTTP_REFERER', 'news:admin_dashboard'))
    
    return redirect('news:admin_dashboard')
