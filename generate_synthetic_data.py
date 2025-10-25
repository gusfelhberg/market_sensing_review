"""
Generate synthetic dataset for HCM Market Sensing Dashboard
Creates realistic customer reviews with varying sentiment, including negative feedback
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
random.seed(42)

# Configuration
PRODUCTS = ['Dayforce', 'SAP SF', 'Workday', 'UKG Pro', 'ADP WFN']
INDUSTRIES = [
    'Manufacturing', 'Healthcare', 'Retail', 'Financial Services', 'IT Services',
    'Professional Services', 'Education', 'Hospitality', 'Transportation', 'Government'
]
ROLES = [
    'HRIS Manager', 'HR Director', 'VP of Human Resources', 'CHRO',
    'Payroll Manager', 'HR Business Partner', 'Talent Acquisition Manager',
    'Compensation & Benefits Manager', 'HR Operations Manager', 'IT Director',
    'Senior HR Analyst', 'Director of People Operations'
]
FUNCTIONS = [
    'Human Resources', 'Finance', 'IT', 'Operations', 'Legal and Compliance'
]
FIRM_SIZES = [
    '1-500', '501-1000', '1001-3500', '3501-10000', '10001+'
]
COUNTRIES = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France']

# Additional variety for headlines
POSITIVE_ADJECTIVES = ['Excellent', 'Outstanding', 'Impressive', 'Great', 'Superb', 'Exceptional', 'Remarkable', 'Fantastic', 'Stellar', 'Top-notch', 'Best-in-class', 'World-class']
NEGATIVE_ADJECTIVES = ['Disappointed', 'Frustrated', 'Struggling', 'Concerned', 'Unhappy', 'Dissatisfied', 'Troubled', 'Worried']
MIXED_ADJECTIVES = ['Mixed feelings', 'Pros and cons', 'Good but', 'Decent', 'Adequate', 'Satisfactory', 'Mixed results']
CONTEXTS = ['for {industry}', 'for our needs', 'for large enterprises', 'for mid-market', 'overall', 'solution', 'platform', 'system', 'for the price']

# Review templates for different sentiment levels and dimensions
REVIEW_TEMPLATES = {
    'positive': {
        'product': [
            "The product capabilities are exceptional. The {feature} module is particularly strong, offering {benefit}. We've been able to {achievement}.",
            "Outstanding product features across the board. The {feature} functionality has transformed how we {process}. Highly recommend for {use_case}.",
            "Very impressed with the product's {feature} capabilities. The system handles {complexity} with ease and the {benefit} is remarkable.",
        ],
        'gtm': [
            "The sales process was smooth and professional. Our account team clearly understood our needs and the demo was comprehensive.",
            "Excellent pre-sales experience. The team was knowledgeable and the value proposition was clear from day one.",
            "Great sales and marketing engagement. They took time to understand our business and provided relevant case studies.",
        ],
        'implementation': [
            "Implementation went smoothly with clear project timelines and excellent support from the implementation team.",
            "Our deployment was completed ahead of schedule thanks to the structured methodology and dedicated resources.",
            "The onboarding process was well-organized with comprehensive training and documentation.",
        ],
        'customer_experience': [
            "Customer support has been outstanding. Response times are quick and the support team is knowledgeable.",
            "Excellent ongoing support. Our CSM is proactive and the help desk resolves issues efficiently.",
            "Great customer experience overall. The support portal is easy to use and we get timely responses.",
        ]
    },
    'negative': {
        'product': [
            "The {feature} module is disappointing. Basic functionality like {missing_feature} is missing or difficult to use. This creates significant {pain_point}.",
            "Product has major gaps in {feature} capabilities. We expected {expectation} but got {reality}. This has caused {impact}.",
            "Very frustrated with {feature}. The interface is {issue} and we've had to implement workarounds for {use_case}.",
        ],
        'gtm': [
            "The sales process overpromised and underdelivered. Features discussed during demos are either missing or require expensive add-ons.",
            "Misleading sales presentation. We were told {promise} but reality is {reality}. This has created trust issues.",
            "Poor communication during sales cycle. Questions went unanswered and the pricing structure was unclear.",
        ],
        'implementation': [
            "Implementation was a disaster. Delays, poor communication, and inexperienced consultants. Went {time_overrun} over timeline.",
            "Very difficult deployment. The implementation team lacked expertise in {area} and we had to figure things out ourselves.",
            "Implementation took {duration} instead of promised {promised_duration}. Poor project management and frequent scope creep.",
        ],
        'customer_experience': [
            "Support is severely lacking. Tickets take {duration} to get responses and solutions are often inadequate.",
            "Terrible customer service experience. Our CSM is unresponsive and support tickets get closed without resolution.",
            "Very disappointed with ongoing support. The knowledge base is outdated and phone support wait times are excessive.",
        ]
    },
    'mixed': {
        'product': [
            "Product has strong {feature} capabilities but struggles with {weakness}. Good for {use_case} but needs improvement in {area}.",
            "The {feature} module works well, however {limitation} is a significant issue. Overall decent but room for improvement.",
        ],
        'implementation': [
            "Implementation had its challenges but we eventually got there. Good support from the team but timeline slipped due to {reason}.",
        ],
    }
}

# Specific pain points and topics by product and dimension
PRODUCT_CHARACTERISTICS = {
    'Dayforce': {
        'strengths': ['Workforce Management', 'Payroll', 'Single Database', 'Real-time Processing'],
        'weaknesses': ['Learning Curve', 'Reporting Complexity', 'Mobile App', 'Third-party Integrations'],
        'common_pain_points': [
            'The platform has a steep learning curve due to its extensive functionality',
            'Custom reporting requires significant training and can be complex',
            'Mobile app could be more intuitive for employee self-service',
            'Integration with third-party systems sometimes requires custom development',
            'Some enhancement requests take time to be prioritized on the roadmap'
        ],
        'positive_aspects': [
            'Single unified database eliminates data synchronization issues',
            'Real-time payroll processing is industry-leading',
            'Workforce management module is comprehensive and flexible',
            'Continuous innovation with regular feature releases',
            'Strong compliance capabilities across multiple jurisdictions'
        ]
    },
    'SAP SF': {
        'strengths': ['Talent Management', 'Learning', 'Enterprise Integration', 'Global Reach'],
        'weaknesses': ['User Interface', 'Configuration Complexity', 'Cost', 'Payroll'],
        'common_pain_points': [
            'User interface feels outdated compared to modern SaaS applications',
            'Configuration requires specialized SAP knowledge and can be complex',
            'Total cost of ownership is high with modules priced separately',
            'Payroll capabilities are weaker compared to specialized solutions',
            'Upgrade cycles can be disruptive to operations'
        ],
        'positive_aspects': [
            'Excellent talent management and succession planning features',
            'Learning management system is best-in-class',
            'Deep integration with SAP ERP ecosystem',
            'Strong global presence with local compliance',
            'Comprehensive analytics and reporting'
        ]
    },
    'Workday': {
        'strengths': ['User Experience', 'Financial Integration', 'Analytics', 'Cloud Architecture'],
        'weaknesses': ['Customization', 'Reporting', 'Time Tracking', 'Cost'],
        'common_pain_points': [
            'Limited customization options compared to on-premise solutions',
            'Reporting can be challenging for complex requirements',
            'Time tracking functionality is basic and may require third-party tools',
            'Premium pricing that may not fit all budgets',
            'Bi-annual updates can introduce unwanted changes'
        ],
        'positive_aspects': [
            'Modern, intuitive user interface with excellent UX',
            'Seamless integration between HR and Finance modules',
            'Strong analytics and data visualization capabilities',
            'Cloud-native architecture with high reliability',
            'Active development with frequent enhancements'
        ]
    },
    'UKG Pro': {
        'strengths': ['Payroll', 'Time and Attendance', 'Industry Solutions', 'Implementation'],
        'weaknesses': ['Modern Features', 'User Interface', 'Analytics', 'Innovation Speed'],
        'common_pain_points': [
            'Some modules feel dated compared to newer cloud solutions',
            'User interface is functional but not as modern as competitors',
            'Advanced analytics capabilities are limited',
            'Slower pace of innovation compared to newer entrants',
            'Mobile experience needs improvement'
        ],
        'positive_aspects': [
            'Excellent payroll processing with high accuracy',
            'Strong time and attendance features',
            'Industry-specific solutions for healthcare, retail, etc.',
            'Implementation process is generally smooth',
            'Reliable and stable platform'
        ]
    },
    'ADP WFN': {
        'strengths': ['Payroll', 'Compliance', 'Scale', 'Support'],
        'weaknesses': ['User Experience', 'Flexibility', 'Integration', 'Reporting'],
        'common_pain_points': [
            'User interface is not intuitive and requires significant training',
            'Limited flexibility in configuring workflows and processes',
            'Integration with third-party applications can be challenging',
            'Reporting capabilities are basic and customization is difficult',
            'System can feel rigid for organizations with unique requirements'
        ],
        'positive_aspects': [
            'Market-leading payroll processing at scale',
            'Excellent compliance and regulatory expertise',
            'Proven ability to handle large, complex organizations',
            'Strong customer support and service organization',
            'Comprehensive benefits administration'
        ]
    }
}

def generate_review_date():
    """Generate a random date in the last 12 months"""
    start_date = datetime(2024, 10, 1)
    end_date = datetime(2025, 10, 24)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

def generate_sentiment_scores(product, overall_rating):
    """Generate sentiment scores across 5 dimensions based on product and overall rating"""
    base_scores = {
        'Dayforce': {'product': 4.2, 'gtm': 4.0, 'market_direction': 4.3, 'implementation': 3.8, 'customer_experience': 4.1},
        'SAP SF': {'product': 4.0, 'gtm': 4.1, 'market_direction': 4.2, 'implementation': 3.6, 'customer_experience': 3.8},
        'Workday': {'product': 4.4, 'gtm': 4.2, 'market_direction': 4.5, 'implementation': 4.0, 'customer_experience': 4.2},
        'UKG Pro': {'product': 3.8, 'gtm': 3.9, 'market_direction': 3.7, 'implementation': 4.1, 'customer_experience': 4.0},
        'ADP WFN': {'product': 3.6, 'gtm': 3.8, 'market_direction': 3.8, 'implementation': 3.7, 'customer_experience': 4.0}
    }
    
    scores = {}
    for dim, base in base_scores[product].items():
        # Add variation based on overall rating with more randomness
        adjustment = (overall_rating - 4) * 0.4
        score = base + adjustment + random.uniform(-0.5, 0.5)
        scores[dim] = max(1, min(5, round(score)))
    
    return scores

def generate_review(product, sentiment_type='mixed', index=0):
    """Generate a complete review for a product with unique content"""
    date = generate_review_date()
    
    # Generate reviewer attributes
    role = random.choice(ROLES)
    industry = random.choice(INDUSTRIES)
    function = random.choice(FUNCTIONS)
    firm_size = random.choice(FIRM_SIZES)
    country = random.choice(COUNTRIES)
    
    # Generate ratings
    if sentiment_type == 'positive':
        overall_rating = random.choice([4, 4, 5, 5, 5])
    elif sentiment_type == 'negative':
        overall_rating = random.choice([1, 2, 2, 3, 3])
    else:
        overall_rating = random.choice([3, 3, 4, 4])
    
    # Generate dimension scores with more variation
    sentiment_scores = generate_sentiment_scores(product, overall_rating)
    
    # Generate other ratings with more variance
    eval_contracting = overall_rating + random.choice([-1, -1, 0, 0, 1])
    integration_deployment = overall_rating + random.choice([-2, -1, 0, 0, 1])
    service_support = overall_rating + random.choice([-1, 0, 0, 1, 1])
    product_capabilities = overall_rating + random.choice([-1, -1, 0, 1, 1])
    
    # Ensure ratings are within 1-5 range
    eval_contracting = max(1, min(5, eval_contracting))
    integration_deployment = max(1, min(5, integration_deployment))
    service_support = max(1, min(5, service_support))
    product_capabilities = max(1, min(5, product_capabilities))
    
    # Generate unique content based on product characteristics
    char = PRODUCT_CHARACTERISTICS[product]
    
    # Create more varied headlines and comments
    strength_areas = char['strengths']
    weakness_areas = char['weaknesses']
    
    if sentiment_type == 'positive':
        # Generate truly unique positive headlines by combining multiple random elements
        adj = random.choice(POSITIVE_ADJECTIVES)
        strength1 = random.choice(strength_areas)
        strength2 = random.choice([s for s in strength_areas if s != strength1])
        context = random.choice(CONTEXTS).format(industry=industry)
        
        headline_patterns = [
            f"{adj} {strength1} - Highly Recommend",
            f"{adj} {strength1} {context}",
            f"{strength1} capabilities exceeded expectations",
            f"Impressed with {product}'s {strength1} features",
            f"Game changer for our {strength1} needs - {firm_size} company",
            f"{adj} {strength1} platform",
            f"Transformed our {industry.lower()} operations with {strength1}",
            f"{strength1} and {strength2} work seamlessly together",
            f"Strong {strength1} and {strength2} make {product} a winner",
            f"{adj} choice for {strength1} in {industry}",
            f"{strength1}: {product} delivers {context}",
            f"Very satisfied with {strength1} and {strength2}",
            f"{product}'s {strength1} is {adj.lower()} - {industry} perspective",
            f"{firm_size} {industry} company loves the {strength1}",
            f"{strength1} excellence makes {product} stand out",
            f"After 1 year: {strength1} continues to impress"
        ]
        headline = random.choice(headline_patterns)
        
        # Varied positive comments
        positive_aspect = random.choice(char['positive_aspects'])
        strength1 = random.choice(strength_areas)
        strength2 = random.choice([s for s in strength_areas if s != strength1])
        
        comment_templates = [
            f"{positive_aspect}. We've been using {product} for our {industry.lower()} organization and the results have been outstanding. The {strength1.lower()} capabilities have transformed our operations. ",
            f"After evaluating multiple vendors, {product} stood out for {strength1.lower()} excellence. {positive_aspect}. Our {firm_size} employee organization has seen significant improvements in efficiency and user satisfaction. ",
            f"As a {role} in {industry.lower()}, I'm very pleased with {product}. The {strength1.lower()} and {strength2.lower()} modules work seamlessly together. {positive_aspect}. Would definitely recommend. ",
            f"{product} has exceeded our expectations across the board. {positive_aspect}. The {strength1.lower()} features have been particularly impressive, allowing us to streamline processes that were previously manual and time-consuming. ",
            f"Our experience with {product} has been overwhelmingly positive. The {strength1.lower()} capabilities are industry-leading. {positive_aspect}. The platform has delivered strong ROI for our {industry.lower()} company. ",
            f"Migrated from a legacy system and couldn't be happier. {product}'s {strength1.lower()} functionality is exactly what we needed. {positive_aspect}. The difference in productivity has been remarkable. ",
            f"{positive_aspect}. The {strength1.lower()} module addresses our complex requirements while maintaining ease of use. As a {firm_size} employee {industry.lower()} organization, scalability and reliability are critical - {product} delivers on both. ",
            f"Very satisfied with our decision to implement {product}. {positive_aspect}. The {strength1.lower()} and {strength2.lower()} features have enabled us to modernize our HR operations and improve the employee experience significantly. "
        ]
        comment = comment_templates[index % len(comment_templates)]
        
        lessons_templates = [
            f"Invest time in training to maximize the platform's potential. The learning curve is worth it for the capabilities you get.",
            f"Engage with the professional services team early - their expertise accelerated our time to value.",
            f"Take advantage of the community forums and user groups. Lots of best practices to learn from other customers.",
            f"Start with core modules and expand incrementally. Don't try to implement everything at once.",
            f"Allocate adequate resources for testing and UAT. Proper preparation ensures a smooth rollout.",
            f"Build strong relationships with your account team. They can help prioritize your enhancement requests.",
            f"Document your processes before implementation. This clarity helps configuration and change management.",
            f"Plan for ongoing optimization after go-live. The platform has depth that takes time to fully leverage."
        ]
        lessons = lessons_templates[index % len(lessons_templates)]
        
    elif sentiment_type == 'negative':
        # Generate truly unique negative headlines
        adj = random.choice(NEGATIVE_ADJECTIVES)
        weakness1 = random.choice(weakness_areas)
        weakness2 = random.choice([w for w in weakness_areas if w != weakness1])
        
        headline_patterns = [
            f"{adj} with {weakness1}",
            f"{weakness1} issues causing major problems",
            f"Expected better from {product} - {weakness1} lacking",
            f"Struggling with {weakness1} limitations in {industry}",
            f"Serious concerns about {weakness1}",
            f"{weakness1} not as advertised - {firm_size} company view",
            f"{adj} with {weakness1} and support",
            f"Considering alternatives due to {weakness1} problems",
            f"{weakness1} and {weakness2} need serious improvement",
            f"Not recommended: {weakness1} issues persist",
            f"{product} falls short on {weakness1} for {industry}",
            f"After 6 months, still struggling with {weakness1}",
            f"{weakness1} limitations a deal-breaker",
            f"Promised {weakness1} never materialized",
            f"Buyer beware: {weakness1} challenges significant",
            f"{industry} company frustrated with {weakness1}"
        ]
        headline = random.choice(headline_patterns)
        
        # Varied negative comments
        pain_point = random.choice(char['common_pain_points'])
        weakness1 = random.choice(weakness_areas)
        weakness2 = random.choice([w for w in weakness_areas if w != weakness1])
        
        comment_templates = [
            f"{pain_point}. As a {firm_size} employee {industry.lower()} company, we expected better from {product}. The {weakness1.lower()} issues have created significant challenges for our team. ",
            f"Unfortunately, {product} has not met our expectations. {pain_point}. The {weakness1.lower()} problems are impacting our daily operations and user adoption has been poor as a result. ",
            f"Experiencing serious issues with {weakness1.lower()} and {weakness2.lower()}. {pain_point}. Our {role} team spends excessive time on workarounds that shouldn't be necessary with a modern platform. ",
            f"After {random.choice(['6', '9', '12', '18'])} months with {product}, we're reconsidering our decision. {pain_point}. The {weakness1.lower()} challenges have not improved despite multiple escalations to support. ",
            f"The sales pitch promised much more than what we received. {pain_point}. Basic {weakness1.lower()} functionality that was demonstrated is either missing or requires expensive customization. Very disappointing. ",
            f"As someone responsible for {industry.lower()} HR operations, I'm frustrated with {product}. {pain_point}. The {weakness1.lower()} and {weakness2.lower()} deficiencies are forcing us to maintain parallel systems and manual processes. ",
            f"{product} looked good in demos but reality is different. {pain_point}. The {weakness1.lower()} issues are particularly problematic for our {firm_size} employee organization. ROI is questionable at this point. ",
            f"Cannot recommend {product} based on our experience. {pain_point}. We've raised concerns about {weakness1.lower()} repeatedly but see little progress. Considering whether to cut our losses and switch vendors. "
        ]
        comment = comment_templates[index % len(comment_templates)]
        
        lessons_templates = [
            f"Do extensive due diligence during evaluation. Make sure the weaknesses won't impact your specific use case.",
            f"Get everything in writing during sales process. Don't rely on verbal commitments about functionality.",
            f"Insist on detailed demos with your own data and use cases. Generic presentations can be misleading.",
            f"Talk to current customers in your industry before committing. Reference calls should be detailed and candid.",
            f"Have a clear exit strategy and avoid long-term lock-in where possible.",
            f"Budget significantly more than quoted for implementation and customization. Hidden costs add up quickly.",
            f"Test thoroughly during trial period. Issues that seem minor initially can become major problems at scale.",
            f"Negotiate strong SLAs for support and platform performance. Standard terms may not protect you adequately."
        ]
        lessons = lessons_templates[index % len(lessons_templates)]
        
    else:  # mixed
        # Generate truly unique mixed headlines
        strength_area = random.choice(strength_areas)
        weakness_area = random.choice(weakness_areas)
        adj = random.choice(MIXED_ADJECTIVES)
        
        headline_patterns = [
            f"Good {strength_area} but Issues with {weakness_area}",
            f"{strength_area} works well, {weakness_area} needs work",
            f"Mixed results - Strong {strength_area}, weak {weakness_area}",
            f"Decent solution but {weakness_area} is problematic",
            f"{strength_area} capabilities solid, concerns about {weakness_area}",
            f"Pros and cons - {strength_area} excellent, {weakness_area} lacking",
            f"Satisfied with {strength_area}, disappointed with {weakness_area}",
            f"{product} has potential but {weakness_area} holding it back",
            f"{adj}: {strength_area} impresses, {weakness_area} frustrates",
            f"{industry} view: {strength_area} strong, {weakness_area} weak",
            f"Solid {strength_area} offset by {weakness_area} challenges",
            f"{firm_size} company: {strength_area} works, {weakness_area} doesn't",
            f"Love the {strength_area}, hate the {weakness_area}",
            f"{strength_area} excellence can't overcome {weakness_area} issues",
            f"Room for improvement despite good {strength_area}",
            f"3 stars: Great {strength_area} but {weakness_area} needs attention"
        ]
        headline = random.choice(headline_patterns)
        
        strength = random.choice(char['positive_aspects'])
        weakness = random.choice(char['common_pain_points'])
        strength_area = random.choice(strength_areas)
        weakness_area = random.choice(weakness_areas)
        
        comment_templates = [
            f"{strength}. However, {weakness.lower()}. Overall, {product} works for our {industry.lower()} organization but there's room for improvement. ",
            f"Our {firm_size} employee {industry.lower()} company has mixed feelings about {product}. The {strength_area.lower()} capabilities are strong and {strength.lower()}. On the flip side, {weakness.lower()}. Decent platform but not perfect. ",
            f"{product} gets some things right and others wrong. {strength}. But we're frustrated that {weakness.lower()}. For the price point, we expected more consistency across all modules. ",
            f"After a year with {product}, I'd say it's a 3.5 out of 5. {strength}. The challenge is that {weakness.lower()}. Works for our core needs but requires workarounds for edge cases. ",
            f"As a {role}, I appreciate {product}'s {strength_area.lower()} features. {strength}. However, {weakness.lower()}. This inconsistency makes planning and training more difficult than it should be. ",
            f"{strength}. This is definitely a positive. Unfortunately, {weakness.lower()}. We're making it work but had higher expectations when we signed the contract. {product} is okay, not great. ",
            f"The good news about {product} is the {strength_area.lower()} functionality. {strength}. The bad news? {weakness}. Our {industry.lower()} organization is adapting but the rough edges are frustrating. ",
            f"I'd describe {product} as solid in some areas, lacking in others. {strength}. That said, {weakness.lower()}. Adequate for our {firm_size} employee company but wouldn't be my first choice if selecting again. "
        ]
        comment = comment_templates[index % len(comment_templates)]
        
        lessons_templates = [
            f"Understand both strengths and limitations before committing. Plan workarounds for known weaknesses.",
            f"Set realistic expectations with stakeholders. Highlight what works well and what will need manual processes.",
            f"Prioritize your requirements carefully. This platform excels in some areas but not others.",
            f"Budget for complementary tools to fill gaps. You may need point solutions for specific needs.",
            f"Join user community to learn best practices. Other customers have solved similar challenges.",
            f"Maintain good relationship with vendor. Ongoing dialogue can influence product roadmap priorities.",
            f"Plan for the long game. Some limitations may improve over time with platform updates.",
            f"Document workarounds clearly. Helps with knowledge transfer and consistency across the team."
        ]
        lessons = lessons_templates[index % len(lessons_templates)]
    
    # Generate varied topics
    all_topics = strength_areas + weakness_areas + ['User Experience', 'ROI', 'Implementation', 'Support', 'Scalability', 'Security', 'Compliance', 'Mobile', 'Reporting', 'Analytics']
    topics = random.sample(all_topics, min(3, len(all_topics)))
    
    # Generate review insights and pain points with more variety
    if sentiment_type == 'positive':
        insights = random.sample(char['positive_aspects'], min(random.randint(2, 4), len(char['positive_aspects'])))
        pain_points = ["Minor: " + random.choice(char['common_pain_points'])] if random.random() > 0.5 else []
    elif sentiment_type == 'negative':
        insights = [random.choice(char['positive_aspects'])] if char['positive_aspects'] and random.random() > 0.3 else ["Some features work adequately"]
        pain_points = random.sample(char['common_pain_points'], min(random.randint(2, 4), len(char['common_pain_points'])))
    else:
        insights = random.sample(char['positive_aspects'], min(random.randint(1, 3), len(char['positive_aspects'])))
        pain_points = random.sample(char['common_pain_points'], min(random.randint(1, 3), len(char['common_pain_points'])))
    
    # Create AI output format
    ai_output = (
        f"Prediction(\n"
        f"    reasoning='{comment[:200]}...',\n"
        f"    product='{sentiment_scores['product']}',\n"
        f"    gtm='{sentiment_scores['gtm']}',\n"
        f"    market_direction='{sentiment_scores['market_direction']}',\n"
        f"    implementation='{sentiment_scores['implementation']}',\n"
        f"    customer_experience='{sentiment_scores['customer_experience']}',\n"
        f"    review_insights='{' '.join(str(i)[:100] for i in insights)}',\n"
        f"    review_pain_points='{' '.join(str(p)[:100] for p in pain_points)}'\n"
        f")"
    )
    
    return {
        'Review Date': date.strftime('%d/%m/%Y'),
        'Review URL': f'https://www.gartner.com/reviews/market/cloud-hcm/vendor/{product.lower().replace(" ", "-")}/product/review-{random.randint(100000, 999999)}',
        'Product': product,
        'Reviewer Role ': role,
        'Reviewer Industry': industry,
        'Reviewer Function': function,
        'Reviewer Firm Size': firm_size,
        'Country': country,
        'Headline': headline,
        'Overall Comment': comment,
        'Lessons Learned': lessons,
        'Overall User Rating': overall_rating,
        'Evaluation & Contracting': eval_contracting if random.random() > 0.2 else None,
        'Integration & Deployment': integration_deployment if random.random() > 0.15 else None,
        'Service & Support': service_support if random.random() > 0.1 else None,
        'Product Capabilities': product_capabilities if random.random() > 0.1 else None,
        'ai_output': ai_output,
        'product': sentiment_scores['product'],
        'gtm': sentiment_scores['gtm'],
        'market_direction': sentiment_scores['market_direction'],
        'implementation': sentiment_scores['implementation'],
        'customer_experience': sentiment_scores['customer_experience'],
        'review_insights': str(insights),
        'review_pain_points': str(pain_points),
        'topics': str(topics),
        'ai_judge_output': 'Prediction(reasoning="Validated review", is_factually_correct=True, is_concise=True, is_relevant=True, is_safe=True)',
        'is_factually_correct': True,
        'is_concise': True,
        'is_relevant': True,
        'is_safe': True
    }

# Generate dataset
print("Generating synthetic dataset...")
reviews = []

# Distribution: Increased volume with more variability
review_distribution = {
    'Dayforce': {'total': 60, 'positive': 24, 'negative': 18, 'mixed': 18},
    'SAP SF': {'total': 55, 'positive': 22, 'negative': 16, 'mixed': 17},
    'Workday': {'total': 50, 'positive': 30, 'negative': 10, 'mixed': 10},
    'UKG Pro': {'total': 35, 'positive': 15, 'negative': 10, 'mixed': 10},
    'ADP WFN': {'total': 35, 'positive': 12, 'negative': 13, 'mixed': 10}
}

for product, dist in review_distribution.items():
    print(f"Generating {dist['total']} reviews for {product}...")
    
    index = 0
    for _ in range(dist['positive']):
        reviews.append(generate_review(product, 'positive', index))
        index += 1
    
    for _ in range(dist['negative']):
        reviews.append(generate_review(product, 'negative', index))
        index += 1
    
    for _ in range(dist['mixed']):
        reviews.append(generate_review(product, 'mixed', index))
        index += 1

# Create DataFrame and shuffle
df = pd.DataFrame(reviews)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to Excel
output_file = 'market_sensing_data_synthetic.xlsx'
df.to_excel(output_file, index=False)

print(f"\n✅ Generated {len(df)} synthetic reviews")
print(f"📊 Distribution by product:")
for product in PRODUCTS:
    count = len(df[df['Product'] == product])
    print(f"   {product}: {count} reviews")

print(f"\n💾 Saved to: {output_file}")

# Show summary statistics
print(f"\n📈 Average sentiment scores:")
for dim in ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']:
    print(f"   {dim}: {df[dim].mean():.2f}")

print(f"\n⭐ Overall rating distribution:")
print(df['Overall User Rating'].value_counts().sort_index())
