from decouple import config

SECRET_KEY = config('SECRET_KEY')

# Database
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': config('MYSQL_DATABASE'),
		'USER': config('MYSQL_USER'),
		'PASSWORD': config('MYSQL_PASSWORD'),
		'HOST': config('DB_HOST', 'db'),
		'PORT': config('DB_PORT', '3306'),
	}
}