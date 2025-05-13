# from django.utils import translation
# from django.conf import settings
# import logging

# logger = logging.getLogger(__name__)

# # middleware.py
# from django.utils.deprecation import MiddlewareMixin
# # from django.conf import settings
# # import logging

# # logger = logging.getLogger(__name__)

# class LanguagePreferenceMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         if request.user.is_authenticated:
#             preferred = getattr(request.user, 'preferred_language', None)
#             if preferred:
#                 if request.session.get(settings.LANGUAGE_COOKIE_NAME) != preferred:
#                     request.session[settings.LANGUAGE_COOKIE_NAME] = preferred
#                     logger.debug(f"Set session language to user's preference: {preferred}")


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

# class LanguagePreferenceMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         language = None

#         session_language = request.session.get(settings.LANGUAGE_COOKIE_NAME)
#         logger.debug(f"Language in session: {session_language}")

#         if session_language:
#             language = session_language
#             logger.debug(f"Using language from session: {language}")
#         elif request.user.is_authenticated and hasattr(request.user, 'preferred_language') and request.user.preferred_language:
#             language = request.user.preferred_language
#             logger.debug(f"Using user preferred language: {language}")
#             request.session[settings.LANGUAGE_COOKIE_NAME] = language
#         else:
#             # fallback to default
#             language = settings.LANGUAGE_CODE
#             logger.debug(f"Using default language: {language}")

#         translation.activate(language)
#         request.LANGUAGE_CODE = language

#         response = self.get_response(request)
#         return response
