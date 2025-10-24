from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin

from .models import Article, Category, Tag, Comment, Newsletter, ContactMessage, UserProfile, Analytics
from .forms import (
    CustomUserCreationForm, UserProfileForm, CommentForm, ReplyForm,
    ContactForm, NewsletterForm, ArticleSearchForm, ArticleForm, UserUpdateForm
)


class HomeView(ListView):
    """Homepage view with featured and recent articles"""
    model = Article
    template_name = 'news/home.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        return Article.objects.filter(
            status='published',
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured articles
        context['featured_articles'] = Article.objects.filter(
            status='published',
            is_published=True,
            featured__in=['featured', 'trending', 'breaking']
        ).select_related('author', 'category').prefetch_related('tags')[:6]
        
        # Trending articles (most viewed in last 7 days)
        week_ago = timezone.now() - timezone.timedelta(days=7)
        context['trending_articles'] = Article.objects.filter(
            status='published',
            is_published=True,
            published_at__gte=week_ago
        ).order_by('-view_count').select_related('author', 'category')[:5]
        
        # Categories with article counts
        context['categories'] = Category.objects.filter(
            is_active=True
        ).annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        ).order_by('-article_count')[:8]
        
        # Recent comments
        context['recent_comments'] = Comment.objects.filter(
            is_approved=True
        ).select_related('author', 'article').order_by('-created_at')[:5]
        
        return context


class ArticleListView(ListView):
    """List view for all articles with filtering and search"""
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Article.objects.filter(
            status='published',
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Tag filter
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Date range filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(published_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(published_at__date__lte=date_to)
        
        return queryset.order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET)
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.all()[:20]
        return context


class ArticleDetailView(DetailView):
    """Detailed view for individual articles"""
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Article.objects.filter(
            status='published',
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Increment view count
        article.increment_view_count()
        
        # Related articles
        context['related_articles'] = article.get_related_articles()
        
        # Comments
        context['comments'] = Comment.objects.filter(
            article=article,
            is_approved=True,
            parent=None
        ).select_related('author').prefetch_related('replies__author')
        
        # Comment form
        context['comment_form'] = CommentForm()
        
        # Social sharing data
        context['share_url'] = self.request.build_absolute_uri(article.get_absolute_url())
        context['share_title'] = article.title
        context['share_description'] = article.excerpt
        
        return context


class CategoryDetailView(ListView):
    """Category detail view with articles"""
    model = Article
    template_name = 'news/category_detail.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Article.objects.filter(
            category=self.category,
            status='published',
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """Tag detail view with articles"""
    model = Article
    template_name = 'news/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Article.objects.filter(
            tags=self.tag,
            status='published',
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class SearchView(ListView):
    """Advanced search view"""
    model = Article
    template_name = 'news/search.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        form = ArticleSearchForm(self.request.GET)
        queryset = Article.objects.filter(
            status='published',
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
        
        if form.is_valid():
            query = form.cleaned_data.get('query')
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(excerpt__icontains=query) |
                    Q(tags__name__icontains=query)
                ).distinct()
            
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            tags = form.cleaned_data.get('tags')
            if tags:
                queryset = queryset.filter(tags__in=tags).distinct()
            
            date_from = form.cleaned_data.get('date_from')
            if date_from:
                queryset = queryset.filter(published_at__date__gte=date_from)
            
            date_to = form.cleaned_data.get('date_to')
            if date_to:
                queryset = queryset.filter(published_at__date__lte=date_to)
        
        return queryset.order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET)
        return context


# User Authentication Views
class CustomLoginView(LoginView):
    template_name = 'news/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('news:home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('news:home')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('news:home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'news/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('news:profile')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)
    
    return render(request, 'news/profile.html', {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile
    })


# Comment Views
@login_required
@require_POST
def add_comment(request, article_slug):
    """Add comment to article"""
    article = get_object_or_404(Article, slug=article_slug, status='published')
    form = CommentForm(request.POST, user=request.user)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.save()
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Error adding comment. Please try again.')
    
    return redirect('news:article_detail', slug=article_slug)


@login_required
@require_POST
def add_reply(request, comment_id):
    """Add reply to comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    form = ReplyForm(request.POST, user=request.user, parent=parent_comment)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Reply added successfully!')
    else:
        messages.error(request, 'Error adding reply. Please try again.')
    
    return redirect('news:article_detail', slug=parent_comment.article.slug)


# Contact and Newsletter Views
def contact_view(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Send email notification to admin
            try:
                send_mail(
                    f'New Contact Message: {contact.subject}',
                    f'From: {contact.name} ({contact.email})\n\n{contact.message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMINS[0][1] if settings.ADMINS else 'admin@example.com'],
                    fail_silently=False,
                )
            except:
                pass  # Email sending failed, but don't break the form
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('news:contact')
    else:
        form = ContactForm()
    
    return render(request, 'news/contact.html', {'form': form})


def newsletter_subscribe(request):
    """Newsletter subscription view"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter, created = Newsletter.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'frequency': form.cleaned_data['frequency'],
                }
            )
            if not created:
                newsletter.frequency = form.cleaned_data['frequency']
                newsletter.is_active = True
                newsletter.save()
            
            newsletter.categories.set(form.cleaned_data['categories'])
            
            if created:
                messages.success(request, 'Successfully subscribed to newsletter!')
            else:
                messages.info(request, 'Newsletter subscription updated!')
            
            return redirect('news:home')
    else:
        form = NewsletterForm()
    
    return render(request, 'news/newsletter.html', {'form': form})


# Article Management Views (for authenticated users)
class ArticleCreateView(LoginRequiredMixin, CreateView):
    """Create new article"""
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'
    success_url = reverse_lazy('news:home')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Article created successfully!')
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing article"""
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'
    
    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('news:article_detail', kwargs={'slug': self.object.slug})


# API Views for AJAX requests
@require_POST
@csrf_exempt
def increment_share_count(request, article_slug):
    """Increment article share count"""
    try:
        article = Article.objects.get(slug=article_slug)
        article.increment_share_count()
        return JsonResponse({'success': True, 'share_count': article.share_count})
    except Article.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Article not found'})


def about_view(request):
    """About page view"""
    return render(request, 'news/about.html')


def privacy_view(request):
    """Privacy policy view"""
    return render(request, 'news/privacy.html')


def terms_view(request):
    """Terms of service view"""
    return render(request, 'news/terms.html')