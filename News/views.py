from rest_framework import generics
from .models import News
from .serializers import NewsSerializer
from rest_framework.pagination import PageNumberPagination


class NewsPagination(PageNumberPagination):
    page_size = 10


class NewsListOrderedByDate(generics.ListAPIView):
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    pagination_class = NewsPagination


class NewsListOrderedByClick(generics.ListAPIView):
    queryset = News.objects.all().order_by('-click_count')[:10]
    serializer_class = NewsSerializer


class NewsDetail(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)
