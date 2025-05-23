import json
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from unittest.mock import patch, MagicMock
import logging
import pytest

# 外部モジュールをモック
import sys

# 必要なモックだけを設定
# transformersモジュールのモック
transformers_mock = MagicMock()
sys.modules['transformers'] = transformers_mock

# sentence_transformersモジュールのモック
sys.modules['sentence_transformers'] = MagicMock()

# opensearchpyモジュールのモック
sys.modules['opensearchpy'] = MagicMock()

from backend.rag_app.views import query_view, load_model_offline
from backend.rag_app.models import SomeModel, Document

@override_settings(ALLOWED_HOSTS=['testserver'])
class QueryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('query_view')  # rag_app/urls.py で name='query_view' と指定していること

    @patch("backend.rag_app.views.llm_inference")
    @patch("backend.rag_app.views.get_top_k_chunks")
    @patch("backend.rag_app.views.Document.objects.all")
    def test_valid_query(self, mock_documents, mock_get_chunks, mock_llm):
        # モックの設定
        mock_documents_qs = MagicMock()
        mock_documents_qs.exists.return_value = True
        mock_documents.return_value = mock_documents_qs
        
        mock_get_chunks.return_value = ["chunk1", "chunk2"]
        mock_llm.return_value = "This is a test answer"
        
        payload = {"query": "Hello"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.json())

    @patch("backend.rag_app.views.Document.objects.all")
    def test_invalid_json(self, mock_documents):
        # モックの設定
        mock_documents_qs = MagicMock()
        mock_documents_qs.exists.return_value = True
        mock_documents.return_value = mock_documents_qs
        
        # JSON でない文字列を送るなど
        response = self.client.post(self.url, data="Not a JSON", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("backend.rag_app.views.llm_inference")
    @patch("backend.rag_app.views.get_top_k_chunks")
    @patch("backend.rag_app.views.Document.objects.all")
    def test_mocked_chunks(self, mock_documents, mock_get_chunks, mock_llm):
        # モックの設定
        mock_documents_qs = MagicMock()
        mock_documents_qs.exists.return_value = True
        mock_documents.return_value = mock_documents_qs
        
        # get_top_k_chunks の返り値をモックし、特定のデータを返すようにする
        mock_get_chunks.return_value = ["chunk1", "chunk2"]
        mock_llm.return_value = "This is a test answer"
        
        payload = {"query": "test"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)
        mock_get_chunks.assert_called_once()

    @patch("backend.rag_app.views.llm_inference")
    @patch("backend.rag_app.views.os_client")
    @patch("backend.rag_app.views.Document.objects.all")
    def test_es_connection_error(self, mock_documents, mock_es, mock_llm):
        """
        Elasticsearch接続エラーをシミュレート
        """
        # モックの設定
        mock_documents_qs = MagicMock()
        mock_documents_qs.exists.return_value = True
        mock_documents.return_value = mock_documents_qs
        
        # search 呼び出し時に例外を発生させる
        mock_es.search.side_effect = Exception("ES Connection failed")
        mock_llm.return_value = "This is a test answer"
        
        payload = {"query": "hello error"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        # 内部でexcept処理 → 200 or 500 etc. 好みにより実装を変更可
        self.assertEqual(response.status_code, 200, "現在は空リストを返しているため成功扱い")
        self.assertIn("answer", response.json())
        mock_es.search.assert_called_once()

    @patch("backend.rag_app.views.llm_inference")
    @patch("backend.rag_app.views.os_client")
    @patch("backend.rag_app.views.Document.objects.all")
    def test_es_search_ok(self, mock_documents, mock_es, mock_llm):
        """
        Elasticsearchが正常応答するパターン。
        """
        # モックの設定
        mock_documents_qs = MagicMock()
        mock_documents_qs.exists.return_value = True
        mock_documents.return_value = mock_documents_qs
        
        mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"content": "found1"}},
                    {"_source": {"content": "found2"}}
                ]
            }
        }
        mock_llm.return_value = "This is a test answer"
        
        payload = {"query": "test es"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.json())
        mock_es.search.assert_called_once()
