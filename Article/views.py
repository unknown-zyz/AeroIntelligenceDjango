from django.http import JsonResponse
from elasticsearch import Elasticsearch
from rest_framework.views import APIView

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
    def get(self, request):
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


# def create_article(request):
#
#     article_data = {
#         "url": "http://example-news-website.com/article1",
#         "source": "Example News Agency",
#         "publish_date": "2024-03-20T10:00:00Z",
#         "title_en": "Breakthrough in Renewable Energy: New Wind Turbine Design",
#         "title_cn": "\u53ef\u518d\u751f\u80fd\u6e90\u7684\u7a81\u7834\uff1a\u65b0\u578b\u98ce\u529b\u6da1\u8f6e\u673a\u8bbe\u8ba1",
#         "content_en": "Scientists have made a significant breakthrough in renewable energy technology with the introduction of a new wind turbine design. {{image1}} The design, which improves efficiency by 30%, is expected to revolutionize the wind energy sector. {{table1}}",
#         "content_cn": "\u79d1\u5b66\u5bb6\u4eec\u5728\u53ef\u518d\u751f\u80fd\u6e90\u6280\u672f\u4e0a\u53d6\u5f97\u4e86\u91cd\u5927\u7a81\u7834\uff0c\u63a8\u51fa\u4e86\u4e00\u79cd\u65b0\u578b\u98ce\u529b\u6da1\u8f6e\u673a\u8bbe\u8ba1\u3002{{image1}} \u8fd9\u79cd\u8bbe\u8ba1\u63d0\u9ad8\u4e8630%\u7684\u6548\u7387\uff0c\u9884\u8ba1\u5c06\u5f7b\u5e95\u6539\u53d8\u98ce\u80fd\u884c\u4e1a\u3002{{table1}}",
#         "summary": "\u4e00\u79cd\u65b0\u578b\u98ce\u529b\u6da1\u8f6e\u673a\u8bbe\u8ba1\uff0c\u63d0\u9ad8\u4e86\u80fd\u6e90\u6548\u7387\uff0c\u9884\u8ba1\u5c06\u5f71\u54cd\u6574\u4e2a\u98ce\u80fd\u884c\u4e1a\u3002",
#         "images": [
#             {
#                 "image_placeholder": "{{image1}}",
#                 "image_path": "/path/to/images/wind_turbine.jpg",
#                 "image_description": "\u65b0\u578b\u98ce\u529b\u6da1\u8f6e\u673a\u8bbe\u8ba1"
#             }
#         ],
#         "tables": [
#             {
#                 "table_placeholder": "{{table1}}",
#                 "table_content": {
#                     "header": ["Innovation", "Impact"],
#                     "rows": [
#                         ["Efficiency Improvement", "30% increase"],
#                         ["Cost Reduction", "20% cheaper"]
#                     ]
#                 },
#                 "table_description": "\u65b0\u578b\u98ce\u529b\u6da1\u8f6e\u673a\u7684\u4e3b\u8981\u521b\u65b0\u548c\u5f71\u54cd"
#             }
#         ],
#         "tags": ["\u53ef\u518d\u751f\u80fd\u6e90", "\u521b\u65b0"],
#         "read_num": 1523
#     }
#
#     try:
#         es.index(index="article", body=article_data)
#         return JsonResponse({'message': 'Article created successfully'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


