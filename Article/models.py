from elasticsearch_dsl import Document, Text, Date, Object, Keyword

class Article(Document):
    url = Keyword()
    source = Keyword()
    publish_date = Date()
    title_en = Text()
    title_cn = Text()
    content_en = Text()
    content_cn = Text()
    summary = Text()
    images = Object()
    tables = Object()

    class Index:
        name = 'article'
