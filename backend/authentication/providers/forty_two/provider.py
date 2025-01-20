from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FortyTwoAccount(ProviderAccount):
    def to_str(self):
        dflt = super().to_str()
        return self.account.extra_data.get('login', dflt)


class FortyTwoProvider(OAuth2Provider):
    id = '42'
    name = '42'
    account_class = FortyTwoAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'username': data.get('login'),
            'email': data.get('email'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
        }


provider_classes = [FortyTwoProvider]
