from datetime import datetime
from elasticsearch import Elasticsearch

from rest_framework import generics, status
from rest_framework.response import Response

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
            article_id = record['article_id']
            es = Elasticsearch(['http://localhost:9200'])
            query = {
                "query": {
                    "ids": {
                        "values": [article_id]
                    }
                },
                "_source": {
                    "excludes": ["content_en", "content_cn", "images", "tables"]
                }
            }
            record['article'] = es.search(index="article", body=query)
            # record['article'] = es.get(index="article", id=article_id)
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
