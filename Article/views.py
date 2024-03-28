from django.http import JsonResponse
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
import requests
from BrowseRecord.serializers import BrowseRecordSerializer
from BrowseRecord.models import BrowseRecord
from Tools.LoginCheck import login_required
from collections import Counter

es = Elasticsearch(['http://localhost:9200'])


class ArticleListOrderedByDate(APIView):
    def get(self, request):
        # page = int(request.GET.get('page', 1))
        # page_size = 10
        # from_record = (page - 1) * page_size
        query = {
            # "from": from_record,
            # "size": page_size,
            "_source": {
                "excludes": ["content_en", "content_cn", "images", "tables"]
            },
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


class ArticleListOrderedByRead(APIView):
    def get(self, request):
        query = {
            "size": 10,
            "_source": {
                "excludes": ["content_en", "content_cn", "images", "tables"]
            },
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


class ArticleRecommend(APIView):
    @login_required
    # todo:数据有tag后测试
    def get(self, request):
        queryset = BrowseRecord.objects.filter(user_id=request.user.uid).order_by('-timestamp')[:5]
        serializer = BrowseRecordSerializer(queryset, many=True)
        article_ids = [record['article_id'] for record in serializer.data]
        tag_counter = Counter()
        for article_id in article_ids:
            result = es.get(index="article", id=article_id)
            article = result['_source']
            tags = article['tags']
            tag_counter.update(tags)
        top_two_tags = tag_counter.most_common(2)
        if len(top_two_tags) == 0:
            return JsonResponse({'articles': []})
        elif len(top_two_tags) == 1:
            query = {
                "size": 5,
                "_source": {
                    "excludes": ["content_en", "content_cn", "images", "tables"]
                },
                "query": {
                    "match": {"tags": top_two_tags[0][0]}
                }
            }
            result = es.search(index="article", body=query)
            articles = result['hits']['hits']
            return JsonResponse({'articles': articles})
        elif len(top_two_tags) == 2:
            query = {
                "size": 5,
                "_source": {
                    "excludes": ["content_en", "content_cn", "images", "tables"]
                },
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"tags": top_two_tags[0][0]}},
                            {"match": {"tags": top_two_tags[1][0]}}
                        ]
                    }
                }
            }
            result = es.search(index="article", body=query)
            articles = result['hits']['hits']
            return JsonResponse({'articles': articles})


class ArticleDetail(APIView):
    @login_required
    def get(self, request):
        article_id = request.GET.get('article_id')
        result = es.get(index="article", id=article_id)
        article = result['_source']
        if 'read_num' not in article:
            article['read_num'] = 1
        else:
            article['read_num'] += 1
        # todo:后续删掉
        # article['content_cn'] = article['content_en']
        # article['title_cn'] = article['title_en']
        # article['homepage_image_description_cn'] = article['homepage_image_description_en']
        # article['summary'] = article['title_en']
        update_body = {
            "doc": {
                "read_num": article['read_num'],
                # todo:后续删掉
                # "content_cn": article['content_cn'],
                # "title_cn": article['title_cn'],
                # "homepage_image_description_cn": article['homepage_image_description_cn'],
                # "summary": article['summary'],
            }
        }
        es.update(index="article", id=article_id, body=update_body)
        user = request.user
        browse_record_data = {
            'user': user.uid,
            'article_id': article_id,
        }
        browse_record_serializer = BrowseRecordSerializer(data=browse_record_data)
        if browse_record_serializer.is_valid():
            browse_record_serializer.save()
        return JsonResponse(article)


class SearchArticle(APIView):
    @login_required
    def get(self, request):
        keyword = request.GET.get('keyword')
        query = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["title_en", "title_cn", "content_en", "content_cn", "tags", "summary",
                               "homepage_image_description_en", "homepage_image_description_cn"]
                }
            }
        }
        result = es.search(index="article", body=query)
        articles = result['hits']['hits']
        return JsonResponse({'articles': articles})


class ExplainWord(APIView):
    @login_required
    def get(self, request):
        word = request.GET.get('word')
        url = "http://172.16.26.4:6667/explain/"
        query = {"content": word}
        data = {}
        response = requests.post(url, json=query)
        if response.status_code == 200:
            result = response.json()
            data['result'] = result['result']
        else:
            data['status'] = response.status_code
            data['result'] = response.text
        return JsonResponse(data)


def update(request):
    es = Elasticsearch(['http://localhost:9200'])
    translate = "http://172.16.26.4:6667/translate/"
    summary = "http://172.16.26.4:6667/summary/"
    tag = "http://172.16.26.4:6667/tag/"
    query = {
        "size": 1,
        "query": {
            "bool": {
                "must": {
                    "range": {
                        "publish_date": {
                            "gte": "now-7d/d",
                            "lte": "now/d"
                        }
                    }
                },
                "must_not": [
                    {
                        "exists": {
                            "field": "content_cn"
                        }
                    },
                    {
                        "exists": {
                            "field": "title_cn"
                        }
                    },
                    {
                        "exists": {
                            "field": "homepage_image_description_cn"
                        }
                    },
                    {
                        "exists": {
                            "field": "summary"
                        }
                    },
                    {
                        "exists": {
                            "field": "tags"
                        }
                    }
                ]
            }
        }
    }
    result = es.search(index="article", body=query)
    articles = result['hits']['hits']
    for article in articles:
        source = article['_source']
        article_id = source['url']
        print(article_id)
        if 'content_cn' not in source or not source['content_cn']:
            source['content_cn'] = splitContent(
                requests.post(translate, json={"content": ''.join(source['content_en'])}).json()['result'])
        if 'title_cn' not in source or not source['title_cn']:
            source['title_cn'] = requests.post(translate, json={"content": source['title_en']}).json()['result']
        if 'homepage_image_description_cn' not in source or not source['homepage_image_description_cn']:
            source['homepage_image_description_cn'] = \
                requests.post(translate, json={"content": source['homepage_image_description_en']}).json()['result']
        if 'summary' not in source or not source['summary']:
            source['summary'] = requests.post(summary, json={"content": ''.join(source['content_cn'])}).json()['result']
        if 'tags' not in source or not source['tags']:
            source['tags'] = splitTags(
                requests.post(tag, json={"content": ''.join(source['content_cn'])}).json()['result'])
        if 'read_num' not in source or not source['read_num']:
            source['read_num'] = 0
        update_body = {
            "doc": {
                "content_cn": source['content_cn'],
                "title_cn": source['title_cn'],
                "homepage_image_description_cn": source['homepage_image_description_cn'],
                "summary": source['summary'],
                "tags": source['tags'],
                "read_num": source['read_num'],
            }
        }
        es.update(index="article", id=article_id, body=update_body)
    print("-------------\n")
    return JsonResponse({'articles': articles})


def splitContent(string):
    if '\n' in string:
        content = string.split('\n')
        new_content = [line + '\n' for line in content if line.strip()]
        return new_content
    return [string]


def splitTags(string):
    if '：' in string:
        _, tags = string.split('：', 1)
        new_tags = [tag.strip() for tag in tags.split('，')]
        return new_tags
    return [string]
