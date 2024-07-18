from django.urls import path
from .views import (
    FAQListView,
    FAQByCategoryListView,
    LawListView,
)

urlpatterns = [
    path('fqas/', FAQListView.as_view(), name='faq-list'),
    path('fqas/category/<str:category>/', FAQByCategoryListView.as_view(), name='faq-by-category'),
    path('law', LawListView().as_view(), name='law')
]
