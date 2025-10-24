from django.urls import path, include
from . import views

app_name = 'news'

urlpatterns = [
    # Admin URLs
    path('admin-panel/', include('news.admin_urls')),
    # Home and main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    
    # Article views
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Category and tag views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # User authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    
    # Article management (authenticated users)
    path('create-article/', views.ArticleCreateView.as_view(), name='article_create'),
    path('edit-article/<slug:slug>/', views.ArticleUpdateView.as_view(), name='article_update'),
    
    # Comments
    path('articles/<slug:article_slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    
    # Newsletter
    path('newsletter/', views.newsletter_subscribe, name='newsletter'),
    
    # API endpoints
    path('api/share/<slug:article_slug>/', views.increment_share_count, name='increment_share'),
]
