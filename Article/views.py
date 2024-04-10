from django.http import JsonResponse
from elasticsearch import Elasticsearch
from User.models import User
from rest_framework.views import APIView
import requests
from BrowseRecord.serializers import BrowseRecordSerializer
from BrowseRecord.models import BrowseRecord
from Tools.LoginCheck import login_required
from collections import Counter

es = Elasticsearch(['http://localhost:9200'])
TAG_LIST = ['NGAD', '人工智能', '军情前沿', '先进技术', '武器装备', '俄乌战争', '生态构建', '人物故事']


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
                },
                {
                    "url": {
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


class ArticleListByTag(APIView):
    def get(self, request):
        tag = request.GET.get('tag')
        tag_map = {
            1: 'NGAD',
            2: '人工智能',
            3: '军情前沿',
            4: '先进技术',
            5: '武器装备',
            6: '俄乌战争',
            7: '生态构建',
            8: '人物故事',
            9: '其他'
        }
        tag = tag_map[int(tag)]
        query = {
            "size": 100,
            "_source": {
                "excludes": ["content_en", "content_cn", "images", "tables"]
            },
            "query": {
                "terms": {
                    "tags": [tag]
                }
            }
        }
        result = es.search(index="article", body=query)
        articles = result['hits']['hits']
        return JsonResponse({'articles': articles})


# class ArticleRecommend(APIView):
#     @login_required
#     def get(self, request):
#         queryset = BrowseRecord.objects.filter(user_id=request.user.uid).order_by('-timestamp')[:5]
#         serializer = BrowseRecordSerializer(queryset, many=True)
#         article_ids = [record['article_id'] for record in serializer.data]
#         tag_counter = Counter()
#         for article_id in article_ids:
#             result = es.get(index="article", id=article_id)
#             article = result['_source']
#             tags = article['tags']
#             tag_counter.update(tags)
#         top_two_tags = tag_counter.most_common(2)
#         if len(top_two_tags) == 0:
#             return JsonResponse({'articles': []})
#         elif len(top_two_tags) == 1:
#             query = {
#                 "size": 5,
#                 "_source": {
#                     "excludes": ["content_en", "content_cn", "images", "tables"]
#                 },
#                 "query": {
#                     "match": {"tags": top_two_tags[0][0]}
#                 }
#             }
#             result = es.search(index="article", body=query)
#             articles = result['hits']['hits']
#             return JsonResponse({'articles': articles})
#         elif len(top_two_tags) == 2:
#             query = {
#                 "size": 5,
#                 "_source": {
#                     "excludes": ["content_en", "content_cn", "images", "tables"]
#                 },
#                 "query": {
#                     "bool": {
#                         "should": [
#                             {"match": {"tags": top_two_tags[0][0]}},
#                             {"match": {"tags": top_two_tags[1][0]}}
#                         ]
#                     }
#                 }
#             }
#             result = es.search(index="article", body=query)
#             articles = result['hits']['hits']
#             return JsonResponse({'articles': articles})


class ArticleRecommendByTagAndUser(APIView):
    @login_required
    def get(self, request, *args, **kwargs):
        user = request.user
        pref_list = user.tag_pref

        user_list = User.objects.all().values('uid', 'tag_pref')
        print(user_list)
        for u in user_list:
            score = 1.0
            if u['tag_pref'] is None:
                u['score'] = score
                continue
            for tag in TAG_LIST:
                if tag in u['tag_pref'] and tag in pref_list:
                    score += u['tag_pref'][tag] * pref_list[tag]
            if u['uid'] == user.uid:
                score = 0
            u['score'] = score
        # user_list.sort(key=lambda x: x['score'])
        user_list = sorted(user_list, key=lambda x: x['score'])
        uid_list = [u['uid'] for u in user_list[:10]]
        queryset = BrowseRecord.objects.filter(user__in=uid_list).order_by('-timestamp')[:20]
        serializer = BrowseRecordSerializer(queryset, many=True).data
        article_ids = [record['article_id'] for record in serializer]
        art_list = [art for art in article_ids if not BrowseRecord.objects.filter(user=user, article_id=art).exists()]
        # print(art_list)
        query = {
            "query": {
                "terms": {
                    "_id": art_list
                }
            }
        }

        result = es.search(index="article", body=query)
        articles = result['hits']['hits']

        query = {
            "size": 20,
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "_script": {
                        "type": "number",
                        "script": {
                            "source": """
                                            double score = 1.0;
                                            for (int i = 0; i < params.tags.length; i++) {
                                                if (params.prefs != null && doc['tags'].value.contains(params.tags[i]) && params.prefs.containsKey(params.tags[i])) {
                                                    score += params.prefs[params.tags[i]];
                                                }
                                            }
                                            return score * doc['read_num'].value;
                                        """,
                            "lang": "painless",
                            "params": {
                                "tags": TAG_LIST,
                                "prefs": pref_list
                            }
                        },
                        "order": "desc"
                    }
                }
            ]
        }

        result = es.search(index="article", body=query)
        articles += result['hits']['hits']
        articles = articles[:20]
        return JsonResponse({'articles': articles})


def update_pref(user, tags):
    pref_list = user.tag_pref
    # print(pref_list)
    if pref_list is None:
        pref_list = {}
    for tag, pref in pref_list.items():
        pref_list[tag] = pref * 0.9
    for tag in tags:
        if tag in pref_list:
            pref_list[tag] += 1.0
        else:
            pref_list[tag] = 5.0
    user.tag_pref = pref_list
    user.save()
    # print(user.tag_pref)


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
        update_pref(user, article['tags'])
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


