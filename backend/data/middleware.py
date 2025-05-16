# data/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.utils import translation
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LanguagePreferenceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user"):
            return

        if request.user.is_authenticated:
            user_lang = getattr(request.user, 'preferred_language', None)
            if user_lang:
                if request.session.get(settings.LANGUAGE_COOKIE_NAME) != user_lang:
                    request.session[settings.LANGUAGE_COOKIE_NAME] = user_lang
                    logger.debug(f"Overriding session language with user preference: {user_lang}")
                translation.activate(user_lang)
                request.LANGUAGE_CODE = user_lang
            else:
                # Fall back to session if user has no preferred_language
                session_lang = request.session.get(settings.LANGUAGE_COOKIE_NAME)
                translation.activate(session_lang or settings.LANGUAGE_CODE)
                request.LANGUAGE_CODE = session_lang or settings.LANGUAGE_CODE
        else:
            # Anonymous users
            session_lang = request.session.get(settings.LANGUAGE_COOKIE_NAME)
            translation.activate(session_lang or settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = session_lang or settings.LANGUAGE_CODE
