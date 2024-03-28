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
