from .views import *
from django.urls import path

urlpatterns = [
    path('', ArticleListOrderedByDate.as_view()),
    path('read/', ArticleListOrderedByReadSeven.as_view()),
    path('rank/', ArticleListOrderedByReadThirty.as_view()),
    path('tag/', ArticleListByTag.as_view()),
    path('recommend/', ArticleRecommend.as_view()),
    path('detail/', ArticleDetail.as_view()),
    path('search/', SearchArticle.as_view()),
    path('explain/', ExplainWord.as_view()),
    path('chat/', Chat.as_view()),
    path('update/', update),
]
