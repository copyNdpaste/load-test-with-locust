from dotenv import load_dotenv
from repository import Repository


load_dotenv(verbose=True)
from model.station import StationReview
import json

import datetime
import os
import random
import jwt
from locust import between, task, FastHttpUser
from locust.contrib.fasthttp import FastResponse

from log.log import logger


ENV = os.getenv("ENV")
logger.info(f"ENV : {ENV}")


def get_jwt(readable_id, last_reset_date):
    encoded_jwt = jwt.encode(
        payload={
            "lastResetDate": str(last_reset_date),
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(hours=12),
            "fresh": False,
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "type": "access",
            "sub": readable_id,
            "nbf": datetime.datetime.now(tz=datetime.timezone.utc),
            "jti": "eyJ0eXAiOiJKV1QiLCJhbGciOi",
        },
        key=os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    return encoded_jwt


class CreateStationReviewMixin:
    def __init__(self) -> None:
        logger.info("CreateStationReviewMixin")
        self.repository = Repository()

    def create_station_review(self, client):
        review_users = self.repository.get_station_review_users()
        if not review_users:
            return False
        review_user = random.choice(review_users)
        user = review_user[0]
        review: StationReview = review_user[1]
        user_id = user.id
        readable_id = user.readable_id
        last_reset_date = user.last_reset_date
        station_id = review.stat_id
        _jwt = get_jwt(readable_id=readable_id, last_reset_date=last_reset_date)
        response = None
        try:
            response: FastResponse = client.post(
                url="/api/test/stations/report",
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Bearer {_jwt}",
                },
                data={"statId": station_id, "note": "test_report"},
            )
            # logger.debug(response)

            if response.status_code not in [200, 204]:
                raise Exception(
                    f"create_station_review response.status_code : {response.status_code} json : {response.json()}"
                )
        except Exception as e:
            logger.error(f"create_report e : {e} response : {response.__dict__}")
            logger.debug(f"user_id : {user_id}")
            logger.debug(f"station_id : {station_id}")


class GetStationMixin:
    def __init__(self) -> None:
        logger.info("GetStationMixin")

    def get_stations_nearby(self, client):
        random_lat = random.randint(0, b=9999999)
        lat = f"37.{random_lat}"
        random_lng = random.randint(0, 9999999)
        lng = f"126.{random_lng}"
        zoom_level = 14
        data = {"lat": lat, "lng": lng, "zoomLevel": zoom_level}
        response = None

        try:
            response: FastResponse = client.get(
                "/api/test/stations/nearby", params=data
            )

            if response.status_code not in [200, 204]:
                raise Exception(
                    f"get_stations_nearby response.status_code : {response.status_code}"
                )
        except Exception as e:
            logger.error(f"get_stations_nearby e : {e} response : {response.__dict__}")


class UpdateStationReviewMixin:
    def __init__(self) -> None:
        logger.info("UpdateStationReviewMixin")
        self.repository = Repository()

    def update_station_review(self, client):
        review_users = self.repository.get_station_review_users()
        if not review_users:
            return False
        review_user = random.choice(review_users)
        user = review_user[0]
        review: StationReview = review_user[1]
        review_id = review.id
        user_id = user.id
        readable_id = user.readable_id
        last_reset_date = user.last_reset_date

        _jwt = get_jwt(readable_id=readable_id, last_reset_date=last_reset_date)

        logger.info(
            f"user_id : {user_id}, review_id : {review_id}, readable_id : {readable_id}"
        )

        response = None
        try:
            response: FastResponse = client.patch(
                f"/api/test/stations/report/{int(review_id)}",
                data=json.dumps(
                    {
                        "content": "updated_content",
                        # "uuid": f"load-test-{review.s3_uuid}",
                        # "addImageNames": ["1234.jpg"],
                        # "deleteImageNames": ["1234.jpg"],
                    },
                ),
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {_jwt}",
                },
            )
            # logger.debug(f"response : {response}")
            if response.status_code not in [200, 204]:
                raise Exception(
                    f"update_station_review response.status_code : {response.status_code}"
                )
        except Exception as e:
            logger.error(
                f"update_station_review call e : {e} response : {response.__dict__}"
            )
            logger.debug(f"user_id : {user_id}")
            logger.debug(f"review_id : {review_id}")


class DeleteStationReviewMixin:
    wait_time = between(10, 15)

    def __init__(self) -> None:
        logger.info("DeleteStationReviewMixin")
        self.repository = Repository()

    def delete_station_review(self, client):
        review_users = self.repository.get_station_review_users()
        if not review_users:
            return False
        review_user = random.choice(review_users)
        user = review_user[0]
        review: StationReview = review_user[1]
        user_id = user.id
        review_id = review.id
        readable_id = user.readable_id
        last_reset_date = user.last_reset_date
        _jwt = get_jwt(readable_id=readable_id, last_reset_date=last_reset_date)

        response = None
        try:
            response: FastResponse = client.delete(
                f"/api/test/stations/report/{int(review_id)}",
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {_jwt}",
                },
            )
            # logger.debug(f"response : {response}")
            if response.status_code not in [200, 204]:
                raise Exception(
                    f"delete_station_review response.status_code : {response.status_code}"
                )
        except Exception as e:
            logger.error(f"delete_station_review call e : {e}")
            logger.debug(f"user_id : {user_id}")
            logger.debug(f"review_id : {review_id}")


class GetDownloadMixin:

    def get_download_service(self, client):
        response = None

        try:
            response: FastResponse = client.get(
                "/api/test/download/eventBanner?group=event-tab"
            )

            # logger.info(f"get_download_service response : {response.__dict__}")

            if response.status_code not in [200, 204]:
                raise Exception(
                    f"get_download_service response.status_code : {response.status_code} json : {response.json()}"
                )
        except Exception as e:
            logger.error(f"get_download_service e : {e} response : {response.__dict__}")


class EveryChargeUserActions(
    FastHttpUser,
    CreateStationReviewMixin,
    GetStationMixin,
    UpdateStationReviewMixin,
    DeleteStationReviewMixin,
    GetDownloadMixin,
):
    host = os.getenv("API_HOST")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt = None

    def quit(self):
        if ENV == "debug":
            logger.debug("quit")
            self.environment.runner.quit()

    def stop(self):
        if ENV == "debug":
            logger.debug("stop")
            self.environment.runner.stop()

    @task
    def create_station_review(self):
        super().create_station_review(client=self.client)
        self.quit()

    @task
    def get_stations_nearby(self):
        super().get_stations_nearby(client=self.client)

    # @task
    # def update_station_review(self):
    #     super().update_station_review(client=self.client)

    # @task
    # def get_download_event_banner(self):
    #     super().get_download_service(client=self.client)

    # 삭제하면 404가 너무 많이 발생해서 주석처리하고 테스트하기
    # @task
    # def delete_station_review(self):
    #     super().delete_station_review(client=self.client)
    #     self.quit()

    # @task
    # def check_before_execute(self):
    #     # event.listens_for 동작 확인용
    #     # execute
    #     Repository().create_everycard()
    #     # execute, cursor_execute
    #     Repository().get_everycard()


class GetEventMixin:
    def get_event(self, client):
        response = None

        try:
            response: FastResponse = client.get("/test/event/2023/Chuseok")

            if response.status_code not in [200, 204]:
                raise Exception(
                    f"get_event response.status_code : {response.status_code} json : {response.json()}"
                )
        except Exception as e:
            logger.error(f"get_event e : {e} response : {response.__dict__}")


class CacheWalkUserActions(FastHttpUser, GetEventMixin):
    host = os.getenv("WEB_HOST")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def quit(self):
        if ENV == "debug":
            logger.debug("quit")
            self.environment.runner.quit()

    @task
    def get_event(self):
        super().get_event(client=self.client)
        self.quit()
