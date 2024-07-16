from django.urls import path
from .views import (
    FAQListView,
    FAQByCategoryListView
)

urlpatterns = [
    path('fqas/', FAQListView.as_view(), name='faq-list'),
    path('fqas/category/<str:category>/', FAQByCategoryListView.as_view(), name='faq-by-category'),
]
