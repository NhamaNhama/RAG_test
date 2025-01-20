import os
from opensearchpy import OpenSearch

OS_ENDPOINT = os.getenv("ES_ENDPOINT", "https://search-my-opensearch-domain-xxxx.ap-northeast-1.es.amazonaws.com")
INDEX_NAME = "my_japanese_index"

os_client = OpenSearch(
    hosts=[OS_ENDPOINT],
    http_compress=True,
    use_ssl=True,
    verify_certs=True
)

# 既にインデックスがあれば削除する例 (必要に応じてコメントアウト)
if os_client.indices.exists(INDEX_NAME):
    os_client.indices.delete(index=INDEX_NAME)

# kuromoji を使ったアナライザーを定義
settings_body = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "kuromoji_user_dict": {
                    "type": "kuromoji_tokenizer",
                    "mode": "search"
                }
            },
            "analyzer": {
                "my_ja_analyzer": {
                    "type": "custom",
                    "tokenizer": "kuromoji_user_dict",
                    "filter": [
                        "lowercase",
                        "kuromoji_part_of_speech"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "my_ja_analyzer"
            },
            # dense_vector を使うなら例えば "embedding" フィールド
            "embedding": {
                "type": "dense_vector",
                "dims": 768
            }
        }
    }
}

# インデックス作成
response = os_client.indices.create(index=INDEX_NAME, body=settings_body)
print("Index created:", response) 