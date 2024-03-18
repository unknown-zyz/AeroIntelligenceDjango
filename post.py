import requests

url = 'http://127.0.0.1:8000/admin/books/'  # 您需要替换为实际的URL
data = {
    'title': 'Python Programming',
    'author': 'Guido van Rossum',
    'genre': 'Programming'
}

response = requests.post(url, data=data)

if response.status_code == 201:
    print("Book created successfully!")
else:
    print("Failed to create book:", response.text)
