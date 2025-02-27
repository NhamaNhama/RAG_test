import json
import os
import requests
import logging
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from backend.rag_app.models import Document, Embedding
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from django.conf import settings
from transformers import pipeline
from sudachipy import Dictionary  # ← 追加
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import uuid
import pypdf
import docx
from django.core.files.storage import default_storage
import time
from huggingface_hub import hf_hub_download


API_URL = "https://api.anthropic.com/v1/complete"

logger = logging.getLogger(__name__)

# ▼ 追加: 要約モデル使用のため
# まず settings から読み込み、無ければ Parameter Store から取得する例
anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", None)
if not anthropic_key:
    try:
        ssm = boto3.client("ssm", region_name="ap-northeast-1")  # リージョンは適宜変更
        param = ssm.get_parameter(Name="/myapp/anthropic_api_key", WithDecryption=True)
        anthropic_key = param["Parameter"]["Value"]
    except (BotoCoreError, ClientError) as e:
        logger.exception("Parameter Store から Anthropic API キー取得に失敗しました")
        anthropic_key = ""

ANTHROPIC_API_KEY = anthropic_key

# ▼ CloudWatch メトリクス送信用クライアント (例)
cw = boto3.client("cloudwatch", region_name="ap-northeast-1")  # リージョン適宜変更

def put_rag_metric(metric_name: str, value: float):
    """
    CloudWatch カスタムメトリクス送信の例。
    サンプリングやバッチ化も検討し、コストやパフォーマンスに配慮。
    """
    cw.put_metric_data(
        Namespace="MyRAGApp",
        MetricData=[{
            "MetricName": metric_name,
            "Value": value,
            # "Unit": "Count",  # 例: リクエスト数なら "Count"
            # "Dimensions": [{"Name": "Environment", "Value": "Production"}]
        }]
    )

# ▼ Hugging Face Transformers を用いた日本語要約パイプライン (DistilBART)
summary_pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-ja-es")

TOKENIZER = Dictionary(dict_type="core").create()

# Sentence-BERT 等を使うためのモデルロード (sonoisa/sentence-bert-base-ja-mean-tokens)
model = SentenceTransformer("sonoisa/sentence-bert-base-ja-mean-tokens")

# ▼ settings.py などで OS_ENDPOINT, EMBEDDING_INDEX を定義してある想定
ES_ENDPOINT = getattr(settings, "ES_ENDPOINT", "http://localhost:9200")
EMBEDDING_INDEX = getattr(settings, "EMBEDDING_INDEX", "embedding_index")

# HTTP リトライ設定例: Anthropic API 用
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

os_client = OpenSearch(
    hosts=[ES_ENDPOINT],
    http_compress=True,
    use_ssl=True,
    verify_certs=True
)

try:
    health = os_client.cluster.health()
    if not health:
        logger.warning("OpenSearch cluster.health() 結果: 異常または取得不可")
except Exception as e:
    logger.exception("OpenSearch cluster.health() 実行中に例外が発生しました")

def embed_text(text: str) -> list[float]:
    """
    日本語対応 Sentence-BERT で埋め込み。
    """
    if not text.strip():
        return [0.0]*768  # モデル次第でdimが異なる場合あり
    embedding = model.encode([text])
    return embedding[0].tolist()

def summarize_text(text: str) -> str:
    """
    DistilBART (line-corp/line-distilbart-ja-es-news) による日本語要約。
    失敗時は先頭200文字を返す。
    """
    if not text:
        return ""
    try:
        summary_list = summary_pipe(text, max_length=60, min_length=10, do_sample=False)
        if summary_list and "summary_text" in summary_list[0]:
            return summary_list[0]["summary_text"]
        else:
            return text[:200]
    except Exception:
        return text[:200] + "..."

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    コサイン類似度を返す簡易関数。ベクトル長が異なるケースは想定外とする。
    """
    import math
    dot = 0.0
    norm1, norm2 = 0.0, 0.0
    for x, y in zip(vec1, vec2):
        dot += x * y
        norm1 += x*x
        norm2 += y*y
    return dot / (math.sqrt(norm1) * math.sqrt(norm2) + 1e-9)

def get_top_k_chunks(query_text: str, k: int = 3) -> list[str]:
    """
    user_query を日本語埋め込み → OpenSearch スクリプトスコア (cosine) で検索 → 上位 k 件
    """
    user_query_vector = embed_text(query_text)

    os_query = {
        "size": k,  # OpenSearch script_score
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": user_query_vector}
                }
            }
        }
    }

    try:
        resp = os_client.search(index=EMBEDDING_INDEX, body=os_query)
    except Exception as es_err:
        logger.exception("OpenSearch への問い合わせでエラーが発生しました")
        # エラー時は空のリスト等を返すか、例外を伝搬させる形でもOK
        return []

    hits = resp.get("hits", {}).get("hits", [])
    chunks = []
    for h in hits:
        doc_content = h["_source"].get("content", "")
        chunks.append(doc_content)
    return chunks

def llm_inference(user_query: str, context: str) -> str:
    """
    日本語の問い合わせに対応 (Anthropic Claude 3.5 はマルチリンガル対応想定)。
    """
    if not ANTHROPIC_API_KEY:
        return "Anthropic API キーが設定されていません。"

    prompt_text = (
        f"\n\nHuman: 以下のコンテキストを参考に質問に回答してください。\n"
        f"質問: {user_query}\n"
        f"コンテキスト:\n{context}\n\n"
        f"Assistant:"
    )
    payload = {
        "prompt": prompt_text,
        "model": "claude-3.5",
        "max_tokens_to_sample": 300,
        "temperature": 0.5,
    }
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        # session.post でリトライ & タイムアウト設定済み
        res = session.post(API_URL, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        response_data = res.json()
        return response_data.get("completion", "回答が取得できませんでした。")
    except requests.Timeout:
        logger.error("Anthropic API timeout")
        return "Anthropic API へのリクエストがタイムアウトしました"
    except requests.HTTPError as http_err:
        logger.error(f"Anthropic API HTTP error: {http_err}")
        return f"Anthropic API 呼び出しでエラーが発生しました: {http_err}"
    except Exception as e:
        logger.exception("Unknown error in llm_inference")
        return f"API 呼び出しでエラーが発生しました: {e}"

@csrf_exempt
def query_view(request):
    """
    クエリを受け取り、OpenSearch から上位チャンクを取得 → 要約 & Claude3.5 へ渡す。
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_query = data.get('query', '')
            
            # CloudWatch メトリクスに問い合わせ回数を送信 (サンプリングやバッチ化も検討)
            try:
                put_rag_metric("TotalQueries", 1.0)
            except Exception:
                logger.warning("CloudWatch メトリクス送信に失敗しました")

            # DB 取得時も例外を捕捉
            documents = Document.objects.all()
            if not documents.exists():
                logger.warning("No Document found in DB")
            
            # 類似度検索 (OpenSearch)
            top_chunks = get_top_k_chunks(user_query, k=3)

            # 要約
            summarized_chunks = [summarize_text(ch) for ch in top_chunks]
            summarized_context = "\n".join(summarized_chunks)

            # LLM推論
            answer = llm_inference(user_query, summarized_context)
            return JsonResponse({"answer": answer})

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            logger.exception("Unexpected error in query_view")
            return JsonResponse({"error": f"Server error: {e}"}, status=500)

    logger.info("Invalid request method for query_view")
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def upload_document_view(request):
    """
    新規ドキュメントをDBに追加し、OpenSearchにインデックスする簡易例 (テキスト用)。
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()

            if not title or not content:
                return JsonResponse({"error": "タイトルまたは本文が空です"}, status=400)

            # S3 にテキストファイルとして保存 (例)
            s3_client = boto3.client("s3", region_name="ap-northeast-1")
            bucket_name = getattr(settings, "S3_BUCKET", "my-bucket")
            unique_key = str(uuid.uuid4()) + ".txt"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=unique_key,
                Body=content.encode("utf-8")
            )

            # DBに登録 (content は空文字、s3_key にアップロードしたキーを保持)
            doc = Document.objects.create(
                title=title,
                content="", 
                s3_key=unique_key
            )

            # ベクトル生成 (sentence-transformers 等)
            vector = model.encode([content])[0].tolist()

            # Embeddingモデルに保存
            Embedding.objects.create(document=doc, vector=bytes(vector))

            # OpenSearch にインデックス
            os_doc = {
                "title": title,
                "content_s3": f"s3://{bucket_name}/{unique_key}",
                "embedding": vector,
            }
            os_client.index(index=EMBEDDING_INDEX, body=os_doc)

            return JsonResponse({"message": "ドキュメントのアップロードが完了しました。"})
        except Exception as e:
            logger.exception("upload_document_view でエラー発生")
            return JsonResponse({"error": f"エラーが発生しました: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def upload_file_document_view(request):
    """
    PDF/Wordファイルを複数まとめてアップロードし、テキスト抽出 → S3保存 → Embedding → OpenSearch インデックス
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse({"error": "ファイルが選択されていません。"}, status=400)

        results = []

        for file_obj in files:
            filename = file_obj.name.lower()
            try:
                # PDF or DOCX かを判定
                if filename.endswith('.pdf'):
                    text_content = extract_text_from_pdf(file_obj)
                elif filename.endswith('.docx'):
                    text_content = extract_text_from_docx(file_obj)
                else:
                    results.append(f"{filename}: 未対応のファイル形式です。")
                    continue

                if not text_content.strip():
                    results.append(f"{filename}: テキストを抽出できませんでした。")
                    continue

                # S3 にファイルをアップロード
                s3_client = boto3.client("s3", region_name="ap-northeast-1")
                bucket_name = getattr(settings, "S3_BUCKET", "my-bucket")
                unique_key = str(uuid.uuid4()) + "_" + filename
                s3_client.upload_fileobj(file_obj, bucket_name, unique_key)

                # DB Document に登録
                doc = Document.objects.create(
                    title=filename,
                    content="",
                    s3_key=unique_key
                )

                # Embedding を生成
                vector = model.encode([text_content])[0].tolist()
                Embedding.objects.create(document=doc, vector=bytes(vector))

                # OpenSearch に登録
                os_doc = {
                    "title": filename,
                    "content_s3": f"s3://{bucket_name}/{unique_key}",
                    "embedding": vector,
                }
                os_client.index(index=EMBEDDING_INDEX, body=os_doc)

                results.append(f"{filename}: アップロード成功")
            except Exception as file_err:
                logger.exception("Failed to process file: %s", filename)
                results.append(f"{filename}: エラーが発生しました {file_err}")

        return JsonResponse({"message": "完了", "details": results})
    except Exception as e:
        logger.exception("upload_file_document_view でエラー発生")
        return JsonResponse({"error": f"エラーが発生しました: {str(e)}"}, status=500)

def extract_text_from_pdf(file_obj) -> str:
    """ PyPDF2 を使ってPDFのテキストを抽出。 """
    text_output = []
    reader = pypdf.PdfReader(file_obj)
    for page in reader.pages:
        text_output.append(page.extract_text() or "")
    return "\n".join(text_output)

def extract_text_from_docx(file_obj) -> str:
    """ python-docx を使ってWordファイルのテキストを抽出 """
    doc = docx.Document(file_obj)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n.join(paragraphs)
