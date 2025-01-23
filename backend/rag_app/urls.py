from django.urls import path
from .views import query_view
from .views import upload_document_view
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DocumentViewSet, EmbeddingViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'embeddings', EmbeddingViewSet)

urlpatterns = [
    path('query/', query_view, name='query_view'),
    path('upload_document/', upload_document_view, name='upload_document'),
    path('', include(router.urls)),
]
