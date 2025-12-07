from django.core.cache import cache
from django.http import HttpResponseForbidden

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response 

    def __call__(self, request):
        # Define the rate limit values (requests per minute)

        rate_limit = 10  # Adjust as needed
        # print(dir(request))
        # print(request.headers.get('Authorization'))
        rate_limit_key = f"ratelimit:{request.headers.get('Authorization')}"

        request_count = cache.get(rate_limit_key, 0)
        print(request_count, rate_limit)
        if request_count >= rate_limit:
            # User has exceeded the rate limit
            return HttpResponseForbidden("Rate limit exceeded")

        # Increment the request count
        request_count += 1
        cache.set(rate_limit_key, request_count, 60)  # Store count for 1 minute

        response = self.get_response(request)
        return response
