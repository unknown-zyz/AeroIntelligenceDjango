from .views import *
from django.urls import path

urlpatterns = [
    path('', ArticleListOrderedByDate.as_view()),
    path('read/', ArticleListOrderedByRead.as_view()),
    path('detail/', ArticleDetail.as_view()),
    path('search/', SearchArticle.as_view()),
    path('explain/', ExplainWord.as_view()),
]
