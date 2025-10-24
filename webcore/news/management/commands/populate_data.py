from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from news.models import Category, Tag, Article, Comment, UserProfile
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Technology', 'description': 'Latest tech news and innovations', 'color': '#007bff'},
            {'name': 'Politics', 'description': 'Political news and analysis', 'color': '#dc3545'},
            {'name': 'Sports', 'description': 'Sports news and updates', 'color': '#28a745'},
            {'name': 'Business', 'description': 'Business and financial news', 'color': '#ffc107'},
            {'name': 'Health', 'description': 'Health and medical news', 'color': '#17a2b8'},
            {'name': 'Entertainment', 'description': 'Entertainment and celebrity news', 'color': '#6f42c1'},
            {'name': 'Science', 'description': 'Scientific discoveries and research', 'color': '#fd7e14'},
            {'name': 'World', 'description': 'International news and events', 'color': '#20c997'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color'],
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create tags
        tags_data = [
            'AI', 'Machine Learning', 'Climate Change', 'Elections', 'Olympics',
            'Stock Market', 'Vaccines', 'Movies', 'Space', 'Economy',
            'Football', 'Basketball', 'Cryptocurrency', 'Renewable Energy',
            'Healthcare', 'Education', 'Innovation', 'Global Warming'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        # Create additional users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'mike_wilson', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Wilson'},
            {'username': 'sarah_jones', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Jones'},
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                # Create user profile
                UserProfile.objects.create(user=user)
                self.stdout.write(f'Created user: {user.username}')
            users.append(user)
        
        # Get admin user
        try:
            admin_user = User.objects.get(username='admin')
            users.append(admin_user)
        except User.DoesNotExist:
            # Create admin user if it doesn't exist
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            users.append(admin_user)
        
        # Create sample articles
        articles_data = [
            {
                'title': 'Revolutionary AI Technology Transforms Healthcare Industry',
                'content': '''The healthcare industry is experiencing a paradigm shift with the introduction of revolutionary artificial intelligence technologies. These cutting-edge AI systems are not only improving diagnostic accuracy but also streamlining patient care processes.

Dr. Sarah Chen, a leading researcher in medical AI, explains that "the integration of machine learning algorithms in diagnostic imaging has increased accuracy rates by 40% while reducing diagnosis time by 60%." This breakthrough is particularly significant in early cancer detection, where timing is crucial.

The technology works by analyzing thousands of medical images and identifying patterns that might be missed by human eyes. This doesn't replace doctors but enhances their capabilities, allowing them to make more informed decisions faster.

Hospitals across the country are already implementing these systems, with early results showing remarkable improvements in patient outcomes. The technology is also being used to predict patient deterioration, allowing for proactive interventions.

However, experts caution that while AI is a powerful tool, it requires careful implementation and ongoing human oversight. The goal is to augment human expertise, not replace it.''',
                'excerpt': 'Revolutionary AI technology is transforming healthcare with improved diagnostic accuracy and streamlined patient care processes.',
                'category': 'Technology',
                'tags': ['AI', 'Healthcare', 'Innovation'],
                'featured': 'featured'
            },
            {
                'title': 'Global Climate Summit Reaches Historic Agreement',
                'content': '''World leaders have reached a historic agreement at the Global Climate Summit, committing to unprecedented measures to combat climate change. The agreement, signed by 195 countries, sets ambitious targets for carbon reduction and renewable energy adoption.

The summit, held in Geneva, saw intense negotiations over five days, with countries finally agreeing on a comprehensive framework that addresses both mitigation and adaptation strategies. The agreement includes:

- A commitment to achieve net-zero emissions by 2050
- Increased funding for developing countries to transition to clean energy
- Enhanced monitoring and reporting mechanisms
- Stronger penalties for non-compliance

Environmental groups have praised the agreement as a "turning point" in global climate action. "This is the most comprehensive climate agreement in history," said Maria Rodriguez, director of the Global Environmental Initiative.

The agreement also includes provisions for technology transfer and capacity building in developing nations, ensuring that all countries can participate in the global effort to combat climate change.

Implementation will begin immediately, with regular progress reviews scheduled every two years. The success of this agreement will depend on the commitment of all signatory nations to follow through on their promises.''',
                'excerpt': 'World leaders reach historic climate agreement with ambitious targets for carbon reduction and renewable energy adoption.',
                'category': 'World',
                'tags': ['Climate Change', 'Global Warming', 'Renewable Energy'],
                'featured': 'breaking'
            },
            {
                'title': 'Olympic Games Set New Records for Sustainability',
                'content': '''The latest Olympic Games have set new records not just in athletic performance, but also in environmental sustainability. The organizing committee has implemented groundbreaking green initiatives that are being hailed as a model for future international sporting events.

The games achieved carbon neutrality for the first time in Olympic history through a combination of renewable energy sources, carbon offset programs, and innovative waste reduction strategies. All venues were powered by 100% renewable energy, and the Olympic Village featured cutting-edge sustainable design.

Athletes and spectators alike praised the environmental initiatives. "It's inspiring to see how the Olympics can lead by example in environmental responsibility," said gold medalist swimmer Emma Thompson.

Key sustainability achievements include:
- Zero waste to landfill across all venues
- 50% reduction in water usage through smart irrigation systems
- Complete elimination of single-use plastics
- Comprehensive recycling programs

The International Olympic Committee has announced that these sustainability standards will become mandatory for all future Olympic Games, ensuring that environmental responsibility becomes a permanent part of the Olympic movement.

Local communities have also benefited from the green infrastructure, with many sustainability features remaining as permanent improvements to the host city.''',
                'excerpt': 'Olympic Games achieve carbon neutrality and set new sustainability standards for international sporting events.',
                'category': 'Sports',
                'tags': ['Olympics', 'Sustainability', 'Environment'],
                'featured': 'trending'
            },
            {
                'title': 'Stock Market Reaches All-Time High Amid Economic Optimism',
                'content': '''The stock market has reached an all-time high, driven by strong economic indicators and investor optimism about future growth prospects. The major indices have shown consistent gains over the past quarter, reflecting confidence in the economic recovery.

Financial analysts attribute the market's performance to several key factors:
- Strong corporate earnings reports across multiple sectors
- Positive employment data showing continued job growth
- Successful implementation of government infrastructure programs
- Increased consumer spending and business investment

Technology stocks have led the gains, with AI and renewable energy companies showing particularly strong performance. The healthcare sector has also seen significant growth, driven by innovation in medical technology and pharmaceuticals.

However, experts caution investors to remain vigilant about potential risks, including inflation concerns and geopolitical tensions. "While the current market conditions are positive, investors should maintain diversified portfolios and avoid over-concentration in any single sector," advised financial analyst David Park.

The Federal Reserve's monetary policy has been supportive of continued growth, with interest rates remaining at levels that encourage both business investment and consumer spending. The central bank has indicated that it will continue to monitor economic indicators closely and adjust policy as needed.

Small and medium-sized businesses are also benefiting from the economic conditions, with many reporting increased access to capital and improved growth prospects.''',
                'excerpt': 'Stock market reaches all-time high driven by strong economic indicators and investor optimism about future growth.',
                'category': 'Business',
                'tags': ['Stock Market', 'Economy', 'Investment'],
                'featured': 'normal'
            },
            {
                'title': 'Breakthrough in Cancer Treatment Shows Promising Results',
                'content': '''A groundbreaking new cancer treatment has shown remarkable results in clinical trials, offering hope to patients with previously untreatable forms of the disease. The treatment, which combines immunotherapy with targeted gene therapy, has achieved unprecedented success rates.

The clinical trial involved 200 patients with advanced cancer, and the results have exceeded all expectations. Dr. Lisa Martinez, the lead researcher, reports that "we're seeing complete remission in 60% of patients, with another 25% showing significant tumor reduction."

The treatment works by reprogramming the patient's own immune system to recognize and attack cancer cells more effectively. Unlike traditional chemotherapy, this approach targets only cancer cells while leaving healthy cells unharmed, resulting in fewer side effects.

Key benefits of the new treatment include:
- Significantly reduced side effects compared to traditional treatments
- Higher success rates in advanced cancer cases
- Potential for long-term remission
- Applicability to multiple cancer types

The treatment is still in the experimental phase, but the results are so promising that the FDA has granted it "breakthrough therapy" status, which will expedite the approval process. If approved, the treatment could be available to patients within the next two years.

Cancer patients and their families are cautiously optimistic about the news. "This gives us hope that we might finally have a cure for cancer," said patient advocate Robert Kim.''',
                'excerpt': 'Breakthrough cancer treatment shows remarkable results in clinical trials, offering hope for previously untreatable forms of the disease.',
                'category': 'Health',
                'tags': ['Healthcare', 'Cancer', 'Innovation'],
                'featured': 'featured'
            }
        ]
        
        for article_data in articles_data:
            # Find category
            category = Category.objects.get(name=article_data['category'])
            
            # Create article
            article = Article.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                author=random.choice(users),
                category=category,
                status='published',
                is_published=True,
                featured=article_data['featured'],
                published_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                view_count=random.randint(100, 5000),
                share_count=random.randint(10, 500)
            )
            
            # Add tags
            for tag_name in article_data['tags']:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    article.tags.add(tag)
                except Tag.DoesNotExist:
                    # Create tag if it doesn't exist
                    tag = Tag.objects.create(name=tag_name)
                    article.tags.add(tag)
            
            self.stdout.write(f'Created article: {article.title}')
        
        # Create some comments
        articles = Article.objects.all()
        for article in articles[:3]:  # Add comments to first 3 articles
            for i in range(random.randint(2, 5)):
                Comment.objects.create(
                    article=article,
                    author=random.choice(users),
                    content=f'This is a great article! I found it very informative and well-written. Comment #{i+1}',
                    is_approved=True
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
