import os

from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "change_this_in_production"
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
# RAG アプリを入れる
'rag_app',
]
MIDDLEWARE = [
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
]

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True

ES_ENDPOINT = os.getenv("ES_ENDPOINT", "http://localhost:9200")
EMBEDDING_INDEX = os.getenv("EMBEDDING_INDEX", "embedding_index")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
STATIC_URL = "/static/"

USE_TZ = False

#ES_ENDPOINT = os.getenv("ES_ENDPOINT", "http://localhost:9200")
#EMBEDDING_INDEX = os.getenv("EMBEDDING_INDEX", "embedding_index")

#ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# 必要に応じて他の設定や環境変数を追加
# 例:
# DB_NAME = os.getenv("DB_NAME", "my_db")
# DB_USER = os.getenv("DB_USER", "user")
# DB_PASS = os.getenv("DB_PASS", "secret") 