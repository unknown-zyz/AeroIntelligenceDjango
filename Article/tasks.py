from time import strftime, localtime
import requests
from elasticsearch import Elasticsearch

def test(day):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " " + day)

def update(day):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    es = Elasticsearch(['http://localhost:9200'])
    translate = "http://172.16.26.4:6667/translate/"
    summary = "http://172.16.26.4:6667/summary/"
    tag = "http://172.16.26.4:6667/tag/"
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
        if 'content_cn' not in source:
            # todo:存的时候是否要转成数组
            source['content_cn'] = requests.post(translate, json={"content": ''.join(source['content_en'])})
        if 'title_cn' not in source:
            source['title_cn'] = requests.post(translate, json={"content": source['title_en']})
        if 'homepage_image_description_cn' not in source:
            source['homepage_image_description_cn'] = \
                requests.post(translate, json={"content": source['homepage_image_description_en']})
        if 'summary' not in source:
            source['summary'] = requests.post(summary, json={"content": source['content_cn']})
        if 'tags' not in source:
            source['tags'] = requests.post(tag, json={"content": source['content_cn']})
            # todo:删冒号，可能有多个tag
        if 'read_num' not in source:
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