import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import logging
from backend.rag_app.views import QueryView
from backend.rag_app.models import SomeModel, User, Document, Embedding
import pytest
from huggingface_hub import hf_hub_download

class QueryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('query_view')  # rag_app/urls.py で name='query_view' と指定していること

    def test_valid_query(self):
        payload = {"query": "Hello"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.json())

    def test_invalid_json(self):
        # JSON でない文字列を送るなど
        response = self.client.post(self.url, data="Not a JSON", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("backend.rag_app.views.get_top_k_chunks")
    def test_mocked_chunks(self, mock_get_chunks):
        # get_top_k_chunks の返り値をモックし、特定のデータを返すようにする
        mock_get_chunks.return_value = ["chunk1", "chunk2"]
        payload = {"query": "test"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)
        mock_get_chunks.assert_called_once()

    @patch("backend.rag_app.views.es")
    def test_es_connection_error(self, mock_es):
        """
        Elasticsearch接続エラーをシミュレート
        """
        # search 呼び出し時に例外を発生させる
        mock_es.search.side_effect = Exception("ES Connection failed")

        payload = {"query": "hello error"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        # 内部でexcept処理 → 200 or 500 etc. 好みにより実装を変更可
        self.assertEqual(response.status_code, 200, "現在は空リストを返しているため成功扱い")
        self.assertIn("answer", response.json())
        mock_es.search.assert_called_once()

    @patch("backend.rag_app.views.es")
    def test_es_search_ok(self, mock_es):
        """
        Elasticsearchが正常応答するパターン。
        """
        mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"content": "found1"}},
                    {"_source": {"content": "found2"}}
                ]
            }
        }
        payload = {"query": "test es"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.json())
        mock_es.search.assert_called_once()

class UserViewSetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('user-list')

    def test_create_user(self):
        payload = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")

    def test_list_users(self):
        User.objects.create(username="user1", email="user1@example.com", password="password1")
        User.objects.create(username="user2", email="user2@example.com", password="password2")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

class DocumentViewSetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('document-list')

    def test_create_document(self):
        payload = {"title": "Test Document", "content": "This is a test document."}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.get().title, "Test Document")

    def test_list_documents(self):
        Document.objects.create(title="Doc1", content="Content1")
        Document.objects.create(title="Doc2", content="Content2")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

class EmbeddingViewSetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('embedding-list')
        self.document = Document.objects.create(title="Doc1", content="Content1")

    def test_create_embedding(self):
        payload = {"document": self.document.id, "vector": b"vector_data"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Embedding.objects.count(), 1)
        self.assertEqual(Embedding.objects.get().document, self.document)

    def test_list_embeddings(self):
        Embedding.objects.create(document=self.document, vector=b"vector1")
        Embedding.objects.create(document=self.document, vector=b"vector2")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

def test_query_view():
    # テストコード
    ... 

def test_download():
    model_path = hf_hub_download(
        repo_id="some-repo",
        filename="some-file"
    )
    ... 

def test_something():
    model_path = hf_hub_download(repo_id="some-repo", filename="some-file")
    ... 
