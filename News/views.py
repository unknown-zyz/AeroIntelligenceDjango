from rest_framework import generics
from .models import News
from .serializers import NewsSerializer
from BrowseRecord.serializers import BrowseRecordSerializer
from rest_framework.pagination import PageNumberPagination
from Tools.LoginCheck import login_required
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


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

    @login_required
    def retrieve(self, request, *args, **kwargs):
        news = self.get_object()
        news.click_count += 1
        news.save()
        user = request.user
        browse_record_data = {
            'user': user.uid,
            'news': news.id,
        }
        browse_record_serializer = BrowseRecordSerializer(data=browse_record_data)
        if browse_record_serializer.is_valid():
            browse_record_serializer.save()
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(browse_record_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
