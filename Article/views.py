from django.http import JsonResponse
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
import requests
from BrowseRecord.serializers import BrowseRecordSerializer
from Tools.LoginCheck import login_required

es = Elasticsearch(['http://localhost:9200'])


class ArticleListOrderedByDate(APIView):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = 10
        from_record = (page - 1) * page_size
        query = {
            "from": from_record,
            "size": page_size,
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "publish_date": {
                        "order": "desc"
                    }
                }
            ]
        }
        result = es.search(index="article", body=query)
        articles = result['hits']['hits']
        return JsonResponse({'articles': articles})


class ArticleListOrderedByRead(APIView):
    def get(self, request):
        query = {
            "size": 10,
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "read_num": {
                        "order": "desc"
                    }
                }
            ]
        }
        result = es.search(index="article", body=query)
        articles = result['hits']['hits']
        return JsonResponse({'articles': articles})


class ArticleDetail(APIView):
    @login_required
    def get(self, request, article_id):
        result = es.get(index="article", id=article_id)
        # 是否需要 read_num+1
        user = request.user
        browse_record_data = {
            'user': user.uid,
            'article_id': article_id,
        }
        browse_record_serializer = BrowseRecordSerializer(data=browse_record_data)
        if browse_record_serializer.is_valid():
            browse_record_serializer.save()
        return JsonResponse(result['_source'])


class SearchArticle(APIView):
    @login_required
    def post(self, request):
        keyword = request.GET.get('keyword')
        query = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["title_en", "title_cn", "content_en", "content_cn"]
                }
            }
        }
        result = es.search(index="article", body=query)
        articles = result['hits']['hits']
        return JsonResponse({'articles': articles})

class SummaryArticle(APIView):
    @login_required
    def post(self, request, article_id):
        result = es.get(index="article", id=article_id)
        article = result['_source']
        title = article['title_en']
        url = "http://172.16.26.4:6667/chat/"
        query = {"text": title}
        data = {}
        response = requests.post(url, json=query)
        if response.status_code == 200:
            result = response.json()
            data['result'] = result['result']
        else:
            data['status'] = response.status_code
            data['result'] = response.text
        return JsonResponse(data)


