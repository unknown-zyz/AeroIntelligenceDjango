from datetime import datetime

from rest_framework import generics, status
from rest_framework.response import Response

from News.models import News
from News.serializers import NewsSerializer
from Tools.LoginCheck import login_required
from .models import BrowseRecord
from .serializers import BrowseRecordSerializer


class BrowseRecordList(generics.ListAPIView):
    serializer_class = BrowseRecordSerializer

    @login_required
    def list(self, request, *args, **kwargs):
        queryset = BrowseRecord.objects.filter(user_id=request.user.uid)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for record in data:
            news_id = record['news']
            news = News.objects.get(pk=news_id)
            record['news'] = NewsSerializer(news).data
            timestamp_str = record['timestamp']
            timestamp_obj = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            record['timestamp'] = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
        return Response(data)


class BrowseRecordDestroy(generics.DestroyAPIView):
    serializer_class = BrowseRecordSerializer
    queryset = BrowseRecord.objects.all()

    @login_required
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().get(pk=kwargs['pk'], user_id=request.user.uid)
            self.perform_destroy(instance)
            return Response({'Destroy success'}, status=status.HTTP_204_NO_CONTENT)
        except BrowseRecord.DoesNotExist:
            return Response({'error': 'Record does not exist'}, status=status.HTTP_404_NOT_FOUND)
