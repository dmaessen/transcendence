from django.urls import path, include
# from oauth2_provider import urls as oauth2_urls

urlpatterns = [
    # path('accounts/', include('allauth.urls')),  # For general allauth routes
    path('42/', include('authentication.providers.forty_two.urls')),  # Include FortyTwo OAuth routes]
    # path('o/', include(oauth2_urls)),

]