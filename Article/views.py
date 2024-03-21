from elasticsearch import Elasticsearch
from django.http import JsonResponse

es = Elasticsearch(['http://localhost:9200'])

def ArticleListOrderedByDate(request):
    query = {
        "size": 10,
        "query": {
            "range": {
                "publish_date": {
                    "gte": "now-1d/d",
                    "lte": "now/d"
                }
            }
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

def ArticleListOrderedByRead(request):
    query = {
        "size": 10,
        "query": {
            "range": {
                "publish_date": {
                    "gte": "now-1d/d",
                    "lte": "now/d"
                }
            }
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

def ArticleDetail(request, article_id):
    result = es.get(index="article", id=article_id)
    return JsonResponse(result['_source'])
