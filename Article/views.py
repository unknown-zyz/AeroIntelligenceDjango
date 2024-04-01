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


class ArticleListOrderedByReadSeven(APIView):
    def get(self, request):
        query = {
            "size": 10,
            "_source": {
                "excludes": ["content_en", "content_cn", "images", "tables"]
            },
            "query": {
                "range": {
                    "publish_date": {
                        "gte": "now-7d/d",
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


class ArticleListOrderedByReadThirty(APIView):
    def get(self, request):
        query = {
            "size": 10,
            "_source": {
                "excludes": ["content_en", "content_cn", "images", "tables"]
            },
            "query": {
                "range": {
                    "publish_date": {
                        "gte": "now-30d/d",
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


class ArticleRecommend(APIView):
    @login_required
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
        update_body = {
            "doc": {
                "read_num": article['read_num'],
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


class Chat(APIView):
    @login_required
    def get(self, request):
        text = request.GET.get('text')
        url = "http://172.16.26.4:6667/chat/"
        query = {"content": text}
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
    # query = {
    #     "size": 1,
    #     "query": {
    #         "bool": {
    #             "must": {
    #                 "range": {
    #                     "publish_date": {
    #                         "gte": "now-7d/d",
    #                         "lte": "now/d"
    #                     }
    #                 }
    #             },
    #             "must_not": [
    #                 {
    #                     "exists": {
    #                         "field": "content_cn"
    #                     }
    #                 },
    #                 {
    #                     "exists": {
    #                         "field": "title_cn"
    #                     }
    #                 },
    #                 {
    #                     "exists": {
    #                         "field": "homepage_image_description_cn"
    #                     }
    #                 },
    #                 {
    #                     "exists": {
    #                         "field": "summary"
    #                     }
    #                 },
    #                 {
    #                     "exists": {
    #                         "field": "tags"
    #                     }
    #                 }
    #             ]
    #         }
    #     }
    # }
    query = {
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
                "should": [
                    {
                        "bool": {
                            "must_not": {
                                "exists": {"field": "content_cn"}
                            }
                        }
                    },
                    {
                        "bool": {
                            "must_not": {
                                "exists": {"field": "title_cn"}
                            }
                        }
                    },
                    {
                        "bool": {
                            "must_not": {
                                "exists": {"field": "homepage_image_description_cn"}
                            }
                        }
                    },
                    {
                        "bool": {
                            "must_not": {
                                "exists": {"field": "summary"}
                            }
                        }
                    },
                    {
                        "bool": {
                            "must_not": {
                                "exists": {"field": "tags"}
                            }
                        }
                    }
                ]
            }
        },
        "size": 1,
    }
    result = es.search(index="article", body=query)
    articles = result['hits']['hits']
    for article in articles:
        source = article['_source']
        article_id = source['url']
        print(article_id)
        if 'content_cn' not in source or not source['content_cn']:
            source['content_cn'] = []
            for content in source['content_en']:
                if (content.startswith('<image') or content.startswith('<table')) and content.endswith('>'):
                    source['content_cn'].append(content)
                else:
                    source['content_cn'].append(requests.post(translate, json={"content": content}).json()['result'])
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


def splitTags(string):
    if '：' in string:
        _, tags = string.split('：', 1)
        new_tags = []
        tags_list = tags.split('，')
        for tag in tags_list:
            if tag in ['NGAD', '人工智能', '军情前沿', '先进技术', '武器装备', '俄乌战争', '生态构建', '人物故事']:
                new_tags.append(tag)
            else:
                new_tags.append('其他')
        return new_tags
    return [string]
