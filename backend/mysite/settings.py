import os

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "change_this_in_production"
DEBUG = True
WSGI_APPLICATION = "backend.mysite.wsgi.application"
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
# RAG アプリを入れる。
'backend.rag_app',
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
USE_TZ = True

ROOT_URLCONF = "backend.mysite.urls"
ES_ENDPOINT = os.getenv("ES_ENDPOINT", "http://localhost:9200")
EMBEDDING_INDEX = os.getenv("EMBEDDING_INDEX", "embedding_index")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
STATIC_URL = "/static/"

# テスト環境の設定
# テスト実行時は外部モジュールをモック化する
if 'pytest' in sys.modules:
    import sys
    from unittest.mock import MagicMock
    
    # テスト時は実際のモデルをロードしない
    LOAD_ACTUAL_MODELS = False
    
    # テスト用のダミーパス
    TEST_MODEL_PATH = "/tmp/test_model"
else:
    # 本番環境では実際のモデルをロード
    LOAD_ACTUAL_MODELS = True

#ES_ENDPOINT = os.getenv("ES_ENDPOINT", "http://localhost:9200")
#EMBEDDING_INDEX = os.getenv("EMBEDDING_INDEX", "embedding_index")

#ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# 必要に応じて他の設定や環境変数を追加
# 例:
# DB_NAME = os.getenv("DB_NAME", "my_db")
# DB_USER = os.getenv("DB_USER", "user")
# DB_PASS = os.getenv("DB_PASS", "secret") 