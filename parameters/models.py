from django.db import models
class BrandCreation(models.Model):
    logo = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    colors = models.JSONField()  # Store color codes and types as a JSON object
    title_font = models.CharField(max_length=255)
    subtitle_font = models.CharField(max_length=255)
    body_font = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    demographic = models.CharField(max_length=255)
    psychographic = models.CharField(max_length=255)
    audience_interest = models.CharField(max_length=255)
    TONE_CHOICES = [
        ('formal', 'Formal'),
        ('casual', 'Casual'),
        ('playful', 'Playful'),
        ('authoritative', 'Authoritative'),
    ]
    tone_of_voice = models.CharField(max_length=20, choices=TONE_CHOICES)
    MESSAGE_STYLE_CHOICES = [
        ('inspire', 'Inspire'),
        ('educate', 'Educate'),
        ('promote', 'Promote'),
    ]
    message_style = models.CharField(max_length=20, choices=MESSAGE_STYLE_CHOICES)
    VISUAL_STYLE_CHOICES = [
        ('minimalistic', 'Minimalistic'),
        ('bold', 'Bold'),
        ('vibrant', 'Vibrant'),
    ]
    visual_style = models.CharField(max_length=20, choices=VISUAL_STYLE_CHOICES)
    keywords = models.JSONField()  # Store keywords as a JSON object
    cta_text = models.CharField(max_length=255)
    current_campaign = models.CharField(max_length=255)
    season = models.CharField(max_length=255, blank=True, null=True)
    mood = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=255)
    # Advanced fields
    advanced = models.JSONField(default=dict)  # Store advanced options as a JSON object
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

def get_string(instance):
    prompt = (
    f"Generate similar images for the brand '{instance.name}' with the following details:\n"
    f"- Tagline: '{instance.tagline}'\n"
    f"- Industry: '{instance.industry}'\n"
    f"- Demographic: '{instance.demographic}'\n"
    f"- Audience Interest: '{instance.audience_interest}'\n"
    f"- Visual Style: '{instance.visual_style}'\n"
    f"- Keywords: {instance.keywords}\n"
    f"- CTA Text: '{instance.cta_text}'\n"
    f"- Current Campaign: '{instance.current_campaign}'\n"
    f"- Season: '{instance.season}'\n"
    f"- Mood: '{instance.mood}'\n"

)
    return prompt
    
    
