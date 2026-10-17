import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:

    def __init__(self, get_response):
        """Runs when the server starts. Runs once."""
        self.get_response = get_response 

    def __call__(self, request):
        start_time = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start_time

        logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")

        return response