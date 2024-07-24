from django.urls import(
    path,
    include
)

from news.views import (
    NewsIndexThumbnailView,
    NewsArticleDetailView,
    NewsListView,
)

app_name='news'

urlpatterns =[
    path('api/thumbnail/', NewsIndexThumbnailView().as_view(), name='thumbnail'),
    path('api/list/', NewsListView.as_view(), name='list'),
    path('api/news/', NewsArticleDetailView.as_view(), name='detail')
]