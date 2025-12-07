from django.http import HttpResponseForbidden
from ipware import get_client_ip
from django.utils import timezone
from datetime import timedelta

from custom_middleware.models import IpCount

token_add_interval = 20  # seconds
token_bonus = 10
token_reset_interval = 120  # seconds


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        client_ip, is_routable = get_client_ip(request)
        objects = IpCount.objects.filter(ip_address=client_ip)
        print(objects)

        if objects:
            obj = objects[0]

            time_interval = timezone.now() - obj.first_request_time

            if time_interval <= timedelta(seconds=token_reset_interval):

                tokens_count = token_bonus * (
                    (int(time_interval.total_seconds()) // token_add_interval) +
                    1) - obj.tokens_spent

                if tokens_count <= 0:
                    wait_time = token_add_interval - int(
                        (timezone.now() - obj.first_request_time
                        ).total_seconds()) % token_add_interval
                    return HttpResponseForbidden(
                        f"Rate Limit Exceeded. Try after {wait_time} seconds")
                else:
                    obj.tokens_spent += 1
                    obj.save()
            else:
                obj.delete()
                IpCount.objects.create(ip_address=client_ip)
        else:
            IpCount.objects.create(ip_address=client_ip)

        response = self.get_response(request)
        return response
