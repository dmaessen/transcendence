from django.urls import path, include

from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('sign_out', views.sign_out, name= 'sign_out'),
	path('sign_in', views.sign_in, name='sign_in'),
	path('register', views.register, name='register')
    path('42/', include('authentication.providers.forty_two.urls')),  # Include FortyTwo OAuth routes]
]