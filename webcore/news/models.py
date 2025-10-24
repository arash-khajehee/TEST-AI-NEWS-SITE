from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
import uuid


class Category(models.Model):
    """News categories for organizing articles"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tags for articles"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:tag_detail', kwargs={'slug': self.slug})


class Article(models.Model):
    """Main article model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    FEATURED_CHOICES = [
        ('normal', 'Normal'),
        ('featured', 'Featured'),
        ('trending', 'Trending'),
        ('breaking', 'Breaking News'),
    ]

    # Basic fields
    title = models.CharField(max_length=200, validators=[MinLengthValidator(10)])
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(validators=[MinLengthValidator(50)])
    excerpt = models.TextField(max_length=500, blank=True, help_text='Short description for article preview')
    
    # Media
    featured_image = models.ImageField(upload_to='articles/images/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=200, blank=True)
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.CharField(max_length=20, choices=FEATURED_CHOICES, default='normal')
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    # SEO and analytics
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    # Reading time estimation
    reading_time = models.PositiveIntegerField(default=0, help_text='Estimated reading time in minutes')
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'is_published']),
            models.Index(fields=['category', 'published_at']),
            models.Index(fields=['featured', 'published_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        # Calculate reading time (average 200 words per minute)
        word_count = len(self.content.split())
        self.reading_time = max(1, word_count // 200)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            self.is_published = True
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})

    def get_related_articles(self, limit=4):
        """Get related articles based on category and tags"""
        return Article.objects.filter(
            models.Q(category=self.category) | models.Q(tags__in=self.tags.all())
        ).exclude(id=self.id).distinct()[:limit]

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_share_count(self):
        """Increment share count"""
        self.share_count += 1
        self.save(update_fields=['share_count'])


class Comment(models.Model):
    """Comments on articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField(validators=[MinLengthValidator(10)])
    is_approved = models.BooleanField(default=True)
    is_highlighted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Moderation
    is_moderated = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_comments')
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'is_approved']),
            models.Index(fields=['author', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"

    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.filter(is_approved=True).order_by('created_at')

    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None


class Newsletter(models.Model):
    """Newsletter subscription model"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    categories = models.ManyToManyField(Category, blank=True, related_name='newsletter_subscribers')
    frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='weekly')

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Contact form messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name}: {self.subject}"


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Social media
    twitter_handle = models.CharField(max_length=50, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class Analytics(models.Model):
    """Analytics tracking for articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['article', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.article.title} on {self.date}"