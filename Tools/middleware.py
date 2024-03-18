# tools/middleware.py

from django.utils.deprecation import MiddlewareMixin

class CloseCsrfMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.csrf_processing_done = True         # csrf处理完毕
