# from django.http import HttpResponseForbidden
# from ipware import get_client_ip
# from django.utils import timezone
# from datetime import timedelta

# from users.models import IpCount

# token_add_interval = 20  # seconds
# token_bonus = 60
# token_reset_interval = 120  # seconds


# class RateLimitMiddleware:

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):

#         client_ip, is_routable = get_client_ip(request)
#         objects = IpCount.objects.filter(ip_address=client_ip)

#         if objects:
#             obj = objects[0]

#             time_interval = timezone.now() - obj.first_request_time

#             if time_interval <= timedelta(seconds=token_reset_interval):

#                 tokens_count = token_bonus * (
#                     (int(time_interval.total_seconds()) // token_add_interval) +
#                     1) - obj.tokens_spent

#                 if tokens_count <= 0:
#                     wait_time = token_add_interval - int(
#                         (timezone.now() - obj.first_request_time
#                         ).total_seconds()) % token_add_interval
#                     return HttpResponseForbidden(
#                         f"Rate Limit Exceeded. Try after {wait_time} seconds")
#                 else:
#                     obj.tokens_spent += 1
#                     obj.save()
#             else:
#                 obj.delete()
#                 IpCount.objects.update_or_create(
#                     ip_address=client_ip,
#                     defaults={}
#                 )
#         else:
#             IpCount.objects.update_or_create(
#                 ip_address=client_ip,
#                 defaults={}
#             )
#         response = self.get_response(request)
#         return response

from django.db import transaction
from django.db.models import F
from django.http import HttpResponseForbidden
from ipware import get_client_ip
from django.utils import timezone
from datetime import timedelta
from users.models import IpCount


token_add_interval = 20  # seconds
token_bonus = 60
token_reset_interval = 120  # seconds


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        client_ip, _ = get_client_ip(request)
        if not client_ip:
            return self.get_response(request)

        now = timezone.now()

        try:
            with transaction.atomic():
                obj, created = IpCount.objects.select_for_update().get_or_create(
                    ip_address=client_ip,
                    defaults={
                        "first_request_time": now,
                        "tokens_spent": 1,
                    },
                )
                # print("Clinet IP:",client_ip,"\nTokens Spent",obj.tokens_spent)

                time_interval = now - obj.first_request_time

                if time_interval > timedelta(seconds=token_reset_interval):
                    obj.first_request_time = now
                    obj.tokens_spent = 1
                    obj.save()
                else:
                    tokens_count = token_bonus * (
                        (int(time_interval.total_seconds()) // token_add_interval) + 1
                    ) - obj.tokens_spent

                    if tokens_count <= 0:
                        wait_time = token_add_interval - (
                            int(time_interval.total_seconds()) % token_add_interval
                        )
                        return HttpResponseForbidden(
                            f"Rate Limit Exceeded. Try after {wait_time} seconds"
                        )

                    # 🔥 Atomic increment
                    obj.tokens_spent = F("tokens_spent") + 1
                    obj.save()

        except Exception:
            # Never break the app because of rate limiter
            return self.get_response(request)

        return self.get_response(request)