from rest_framework import generics
from .models import BrowseRecord
from .serializers import BrowseRecordSerializer
from News.models import News
from News.serializers import NewsSerializer


class BrowseRecordListCreate(generics.ListCreateAPIView):
    queryset = BrowseRecord.objects.all()
    serializer_class = BrowseRecordSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        data = response.data
        for record in data:
            news_id = record['news']
            news = News.objects.get(pk=news_id)
            record['news'] = NewsSerializer(news).data
        return response


class BrowseRecordDestroy(generics.DestroyAPIView):
    queryset = BrowseRecord.objects.all()
    serializer_class = BrowseRecordSerializer
