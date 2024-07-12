from django.urls import path
from .views import (
    FAQListView,
    FAQByCategoryListView
)

urlpatterns = [
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('faqs/category/<str:category>/', FAQByCategoryListView.as_view(), name='faq-by-category'),
]
