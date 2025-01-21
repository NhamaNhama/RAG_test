import os

ES_ENDPOINT = os.getenv("ES_ENDPOINT", "http://localhost:9200")
EMBEDDING_INDEX = os.getenv("EMBEDDING_INDEX", "embedding_index")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# 必要に応じて他の設定や環境変数を追加
# 例:
# DB_NAME = os.getenv("DB_NAME", "my_db")
# DB_USER = os.getenv("DB_USER", "user")
# DB_PASS = os.getenv("DB_PASS", "secret") 