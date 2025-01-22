from django.db import models

# ▼ 追加: タイムスタンプ用抽象モデル
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 既存の Document モデルを継承
class Document(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    s3_key = models.CharField(max_length=255, blank=True, default="")

# 既存の Embedding モデルを継承
class Embedding(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    vector = models.BinaryField()  # もしくは Float Vector, pgvector拡張など 

class SomeModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name 