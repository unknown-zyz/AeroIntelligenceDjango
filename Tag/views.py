from rest_framework import generics
from .models import Tag
from .serializers import TagSerializer

class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

