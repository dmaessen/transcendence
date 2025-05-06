from django.utils import translation
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LanguagePreferenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current language code from the session or cookie
        current_language = translation.get_language()
        logger.debug(f"Current language: {current_language}")
        
        # Check if language was manually selected via language selector
        session_language = request.session.get(settings.LANGUAGE_COOKIE_NAME)
        logger.debug(f"Language in session: {session_language}")
        
        if session_language:
            # Use the language from session
            language = session_language
            logger.debug(f"Using language from session: {language}")
        elif request.user.is_authenticated and hasattr(request.user, 'preferred_language') and request.user.preferred_language:
            # Use user's preferred language
            language = request.user.preferred_language
            logger.debug(f"Using user preferred language: {language}")
            
            # Don't override if user already selected a language manually
            if not session_language:
                request.session[settings.LANGUAGE_COOKIE_NAME] = language
                translation.activate(language)
        else:
            # Default to system language
            language = settings.LANGUAGE_CODE
            logger.debug(f"Using default language: {language}")
        
        # Set language for this request
        request.LANGUAGE_CODE = language
        
        # Process the request
        response = self.get_response(request)
        return response