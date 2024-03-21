from elasticsearch import Elasticsearch
from django.http import JsonResponse

def search(request):
    es = Elasticsearch()
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

def getDoc(request, article_id):
    es = Elasticsearch()
    result = es.get(index="article", id=article_id)
    return JsonResponse(result['_source'])