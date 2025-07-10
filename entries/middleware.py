from django.utils import translation
from django.conf import settings

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get language from session
        user_language = request.session.get('user_language', 'en')
        
        # Activate the language for this request
        translation.activate(user_language)
        request.LANGUAGE_CODE = user_language
        
        response = self.get_response(request)
        
        # Set the language cookie
        if hasattr(request, 'session') and 'user_language' in request.session:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        
        return response 