from locust import run_single_user
from locustfile import EveryChargeUserActions, CacheWalkUserActions


run_single_user(user_class=EveryChargeUserActions)
# run_single_user(user_class=CacheWalkUserActions)
