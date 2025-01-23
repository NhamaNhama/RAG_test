from django.test import TestCase
from backend.rag_app.models import User, Document, Embedding

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.password, 'password123')

    def test_user_str(self):
        self.assertEqual(str(self.user), self.user.username)

class DocumentModelTest(TestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title='Test Document',
            content='This is a test document.'
        )

    def test_document_creation(self):
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.content, 'This is a test document.')

    def test_document_str(self):
        self.assertEqual(str(self.document), self.document.title)

class EmbeddingModelTest(TestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title='Test Document',
            content='This is a test document.'
        )
        self.embedding = Embedding.objects.create(
            document=self.document,
            vector=b'\x00\x01\x02\x03'
        )

    def test_embedding_creation(self):
        self.assertEqual(self.embedding.document, self.document)
        self.assertEqual(self.embedding.vector, b'\x00\x01\x02\x03')

    def test_embedding_str(self):
        self.assertEqual(str(self.embedding), f'Embedding for {self.document.title}')
