# ベースイメージ
FROM python:3.10-slim AS base

# 環境変数の設定
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# システムパッケージのインストール (openjdkやgit等、必要に応じて調整)
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txt をコピー＆インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Djangoプロジェクト全体をコピー
COPY . .

# ポートを公開 (本番では ALB/ECS のターゲットグループが割り当て)
EXPOSE 8000

# Gunicorn を使ってアプリ起動
# DJANGO_SETTINGS_MODULE で settings.py パスを指定 (mysite/settings など)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mysite.wsgi:application"] 