from tasks import splitTags

source = {"content": "111", "title_cn": "", "summary": "333", "tags": "444", "read_num": "555"}

if 'title_cn' not in source:
    print("err1")
else:
    print(source['title_cn'])

import  requests

result = requests.post("http://172.16.26.4:6667/translate/", json={"content": source['title_en']}).json()['result']
print(result)