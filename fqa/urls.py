from django.urls import path
from .views import (
    FAQListView,
    FAQByCategoryListView,
    LawListView,
    RuleListView,
    GlossaryListView
)

urlpatterns = [
    path('fqas/', FAQListView.as_view(), name='faq-list'),
    path('fqas/category/<str:category>/', FAQByCategoryListView.as_view(), name='faq-by-category'),
    path('law/', LawListView().as_view(), name='law'),
    path('rule/', RuleListView().as_view(), name='rule'),
    path('glossary/', GlossaryListView().as_view(), name='glossary')
]
