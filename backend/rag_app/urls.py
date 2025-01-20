from django.urls import path
from .views import query_view
# from .views import DocumentListView  # 例: クラスベースビューを使う場合

urlpatterns = [
    path('query/', query_view, name='query_view'),
] 