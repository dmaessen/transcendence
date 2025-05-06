from django.utils import translation
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LanguagePreferenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = None

        session_language = request.session.get(settings.LANGUAGE_COOKIE_NAME)
        logger.debug(f"Language in session: {session_language}")

        if session_language:
            language = session_language
            logger.debug(f"Using language from session: {language}")
        elif request.user.is_authenticated and hasattr(request.user, 'preferred_language') and request.user.preferred_language:
            language = request.user.preferred_language
            logger.debug(f"Using user preferred language: {language}")
            request.session[settings.LANGUAGE_COOKIE_NAME] = language
        else:
            # fallback to default
            language = settings.LANGUAGE_CODE
            logger.debug(f"Using default language: {language}")

        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)
        return response
