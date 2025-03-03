import os
import django
from django.conf import settings

# テスト実行前にDjangoの設定を読み込む
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.mysite.settings")
django.setup() 