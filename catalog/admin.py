from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn10', 'rating_avg', 'pages')
    search_fields = ('title', 'author', 'isbn10')
    list_filter = ('language', 'format')
    