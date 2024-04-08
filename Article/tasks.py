from time import strftime, localtime
import requests
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])


def test(day):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " " + day)


def update(day):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    # query = {
    #     "query": {
    #         "bool": {
    #             "must": {
    #                 "range": {
    #                     "publish_date": {
    #                         "gte": f"now-{day}d/d",
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
    #     },
    #     "size": 100,
    # }
    # todo: query有bug
    query = {
        "query": {
            "bool": {
                "must": {
                    "range": {
                        "publish_date": {
                            "gte": f"now-{day}d/d",
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
                            },
                            "must": {
                                "exists": {"field": "homepage_image_description_en"}
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
                ],
                "minimum_should_match": 1
            }
        },
        "size": 1000,
    }
    result = es.search(index="article", body=query, scroll="1m")
    scroll_id = result['_scroll_id']
    processArticles(result['hits']['hits'])
    while True:
        scroll_result = es.scroll(scroll_id=scroll_id, scroll="1m")
        if len(scroll_result['hits']['hits']) == 0:
            break
        processArticles(scroll_result['hits']['hits'])
    es.clear_scroll(scroll_id=scroll_id)
    print("-------------\n")


def updateHomeImage(day):
    day = 60
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "publish_date": {
                                "gte": f"now-{day}d/d",
                                "lte": "now/d"
                            }
                        }
                    },
                    {
                        "exists": {
                            "field": "homepage_image"
                        }
                    },
                    {
                        "term": {
                            "homepage_image": ""
                        }
                    }
                ]
            }
        },
        "size": 1000
    }
    result = es.search(index="article", body=query)
    for article in result['hits']['hits']:
        source = article['_source']
        print(source['url'])
        source['homepage_image'] = "image/default.jpg"
        update_body = {
            "doc": {
                "homepage_image": source['homepage_image']
            }
        }
        try:
            es.update(index="article", id=source['url'], body=update_body)
        except Exception as e:
            print(f"Failed to update document with id {article['_id']}: {e}")
    print("-------------\n")


def processArticles(articles):
    translate = "http://172.16.26.4:6667/translate/"
    summary = "http://172.16.26.4:6667/summary/"
    tag = "http://172.16.26.4:6667/tag/"
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
                    source['content_cn'].append(
                        requests.post(translate, json={"content": content}).json()['result'])
        if 'title_cn' not in source or not source['title_cn']:
            source['title_cn'] = requests.post(translate, json={"content": source['title_en']}).json()['result']
        if ('homepage_image_description_cn' not in source or not source[
            'homepage_image_description_cn']) and 'homepage_image_description_en' in source:
            source['homepage_image_description_cn'] = \
                requests.post(translate, json={"content": source['homepage_image_description_en']}).json()['result']
        content_cn = joinContent(source['content_cn'])
        if len(content_cn) < 5000:
            if 'summary' not in source or not source['summary']:
                source['summary'] = requests.post(summary, json={"content": content_cn}).json()['result']
            if 'tags' not in source or not source['tags']:
                source['tags'] = splitTags(
                    requests.post(tag, json={"content": content_cn}).json()['result'])
        else:
            source['summary'] = ""
            source['tags'] = []
        if 'read_num' not in source or not source['read_num']:
            source['read_num'] = 0
        update_body = {
            "doc": {
                "content_cn": source['content_cn'],
                "title_cn": source['title_cn'],
                "summary": source['summary'],
                "tags": source['tags'],
                "read_num": source['read_num'],
            }
        }
        if 'homepage_image_description_cn' in source:
            update_body['doc']['homepage_image_description_cn'] = source['homepage_image_description_cn']
        try:
            es.update(index="article", id=article_id, body=update_body)
        except Exception as e:
            print(f"Failed to update document with id {article_id}: {e}")


def splitTags(string):
    if '：' in string:
        _, tags = string.split('：', 1)
    else:
        tags = string
    new_tags = []
    tags_list = tags.split('，')
    for tag in tags_list:
        if tag in ['NGAD', '人工智能', '军情前沿', '先进技术', '武器装备', '俄乌战争', '生态构建', '人物故事']:
            new_tags.append(tag)
        elif tag in ["'NGAD'", "'人工智能'", "'军情前沿'", "'先进技术'", "'武器装备'", "'俄乌战争'", "'生态构建'", "'人物故事'"]:
            new_tags.append(tag[1:-1])
        else:
            new_tags.append('其他')
    return new_tags


def joinContent(contents):
    result = []
    for content in contents:
        if (content.startswith('<image') or content.startswith('<table')) and content.endswith('>'):
            continue
        else:
            result.append(content)
    return ''.join(result)
