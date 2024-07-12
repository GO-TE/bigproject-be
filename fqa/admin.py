from django.contrib import admin
from .models import FAQ

class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer', 'category')
    search_fields = ('question', 'answer', 'category')
    
admin.site.register(FAQ, FAQAdmin)