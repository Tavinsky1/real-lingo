# entries/email_verification.py

import uuid
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from .translations import get_translation


def send_verification_email(verification, request, language='en'):
    """Send verification email to the user."""
    verification_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'token': verification.token})
    )
    
    # Get translations
    subject = get_translation('email_verification_subject', language)
    welcome_msg = get_translation('welcome_to_lingoworld', language)
    verify_msg = get_translation('verify_email_message', language)
    verify_button = get_translation('verify_email_button', language)
    
    # Prepare email context
    context = {
        'user': verification.user,
        'verification_url': verification_url,
        'site_name': 'LingoWorld',
        'language': language,
        'subject': subject,
        'welcome_msg': welcome_msg,
        'verify_msg': verify_msg,
        'verify_button': verify_button,
        'expiry_days': getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7)
    }
    
    # Render email templates
    html_message = render_to_string('registration/verification_email.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=f"{subject} - LingoWorld",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[verification.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def create_verification_for_user(user, request, language='en'):
    """Create and send email verification for a user."""
    from .models import EmailVerification
    
    # Create or get verification record
    verification, created = EmailVerification.objects.get_or_create(user=user)
    
    if not created:
        # If verification already exists, generate new token
        verification.token = uuid.uuid4()
        verification.created_at = datetime.now()
        verification.is_verified = False
        verification.verified_at = None
        verification.save()
    
    # Send verification email
    return send_verification_email(verification, request, language)


def send_welcome_email(user):
    from django.core.mail import send_mail
    subject = 'Welcome to LingoWorld'
    message = 'Welcome to LingoWorld! Your account is now active.'
    from_email = 'lingoworldapp@gmail.com'
    recipient_list = [user.email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
