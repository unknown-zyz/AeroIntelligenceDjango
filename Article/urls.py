from .views import *
from django.urls import path

urlpatterns = [
    path('', ArticleListOrderedByDate.as_view()),
    path('read/', ArticleListOrderedByRead.as_view()),
    path('detail/<int:article_id>/', ArticleDetail.as_view()),
    path('search/', SearchArticle.as_view()),
    path('summary/<int:article_id>/', SummaryArticle.as_view()),
    # path('create/', create_article),

]
