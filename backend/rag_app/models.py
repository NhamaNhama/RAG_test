from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

class Document(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    s3_key = models.CharField(max_length=255, blank=True, default="")

class Embedding(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    vector = models.BinaryField()

class SomeModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
