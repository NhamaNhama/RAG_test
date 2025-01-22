from django.contrib import admin
from backend.rag_app.models import SomeModel  # 例

class MyAdminClass(admin.ModelAdmin):
    # 自分自身を再インポートしない
    list_display = ("id", "name")  # 例

admin.site.register(SomeModel, MyAdminClass) 