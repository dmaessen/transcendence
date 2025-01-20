from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.models import SocialLogin
from requests.exceptions import HTTPError

class FortyTwoOAuth2Adapter(OAuth2Adapter):
    provider_id = '42'
    access_token_url = 'https://api.intra.42.fr/oauth/token'
    authorize_url = 'https://api.intra.42.fr/oauth/authorize'
    profile_url = 'https://api.intra.42.fr/v2/me'

    def complete_login(self, request, app, token, **kwargs):
        try:
            resp = self.get_response(self.profile_url, token)
            extra_data = resp.json()
            return self.get_provider().sociallogin_from_response(request, extra_data)
        except (HTTPError, OAuth2Error) as e:
            raise OAuth2Error(f'Error fetching user profile: {e}')

# Expose OAuth2 login and callback as views
# oauth2_login = OAuth2Adapter.oauth2_login
# oauth2_callback = OAuth2Adapter.oauth2_callback
