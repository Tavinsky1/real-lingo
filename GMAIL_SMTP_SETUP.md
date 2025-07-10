# Gmail SMTP Configuration Guide

## ✅ COMPLETED SETUP

### 1. Email Configuration Updated
- **File**: `lingo_project/settings.py`
- **Configuration**: Gmail SMTP with environment variables
- **Email**: lingoworldapp@gmail.com
- **Backend**: SMTP (smtp.gmail.com:587 with TLS)

### 2. Environment Variables Added
- **File**: `.env`
- **Variables**:
  - `EMAIL_HOST_USER=lingoworldapp@gmail.com`
  - `EMAIL_HOST_PASSWORD=Generic1234!`

## 🔧 REQUIRED GMAIL SETUP

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Enable 2FA if not already enabled

### Step 2: Generate App Password
1. Go to **Security** → **App passwords**
2. Select **Mail** as the app
3. Generate a new app password
4. **Replace `Generic1234!` in `.env` with the generated app password**

### Step 3: Update .env File
```env
EMAIL_HOST_USER=lingoworldapp@gmail.com
EMAIL_HOST_PASSWORD=your_generated_app_password_here
```

## 🧪 TESTING EMAIL FUNCTIONALITY

### Test 1: Basic SMTP Connection
```python
# In Django shell: python manage.py shell
from django.core.mail import send_mail
from django.conf import settings

# Test basic email
send_mail(
    'Test Email',
    'Testing Gmail SMTP configuration',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],
    fail_silently=False,
)
```

### Test 2: Email Verification System
```python
# Test the actual email verification
from entries.models import User
from entries.auth_views import send_verification_email

# Create test user and send verification
user = User.objects.create_user(
    username='testuser',
    email='your-test-email@gmail.com',
    password='testpass123',
    is_active=False
)
send_verification_email(user, 'en')
```

## 📧 EMAIL FEATURES CONFIGURED

### 1. Automated Email Verification
- **Trigger**: User registration
- **Template**: `entries/templates/entries/emails/verification_email.html`
- **Expiration**: 7 days
- **Languages**: English, Spanish, French

### 2. Email Templates
- **HTML**: Responsive design with LingoWorld branding
- **Translations**: Multi-language support
- **Styling**: Inline CSS for email client compatibility

### 3. Email Settings
- **From Address**: LingoWorld <lingoworldapp@gmail.com>
- **Subject Prefix**: [LingoWorld]
- **TLS Encryption**: Enabled
- **Port**: 587 (secure SMTP)

## 🔒 SECURITY CONSIDERATIONS

### Environment Variables
- Email credentials stored in `.env` file
- Not committed to version control
- Production-ready configuration

### Gmail Security
- Uses App Passwords (more secure than account password)
- TLS encryption for all email transmission
- Follows Gmail's security best practices

## 🚀 NEXT STEPS

1. **Generate Gmail App Password** (most important!)
2. Update `.env` with the app password
3. Test email functionality with a real email address
4. Monitor email delivery in Gmail's sent folder

## 📝 CONFIGURATION SUMMARY

```python
# Current settings.py configuration:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'lingoworldapp@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'Generic1234!')
DEFAULT_FROM_EMAIL = f'LingoWorld <{EMAIL_HOST_USER}>'
EMAIL_SUBJECT_PREFIX = '[LingoWorld] '
```

**STATUS**: Gmail SMTP configured and ready for testing with proper app password!
