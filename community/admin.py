from django.contrib import admin
# from .models import (
#     Article,
#     Comment,
#     Category,
#     Image,
#     FAQ,
# )
# # Register your models here.

# class ArticleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'user', 'created_at', 'updated_at', 'is_active')
#     list_filter = ('created_at', 'updated_at', 'is_active')
#     search_fields = ('title', 'content')

# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'article', 'user', 'message', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('message',)

# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'major', 'sub')
#     search_fields = ('major', 'sub')

# class ImageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'path', 'created_at')
#     search_fields = ('path',)

# class FAQAdmin(admin.ModelAdmin):
#     list_display = ('id', 'question', 'answer', 'category')
#     search_fields = ('question', 'answer', 'category')
    
# admin.site.register(Article, ArticleAdmin)
# admin.site.register(Comment, CommentAdmin)
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Image, ImageAdmin)
# admin.site.register(FAQ, FAQAdmin)