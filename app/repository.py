from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv

from model.everycard import Everycard

load_dotenv(verbose=True)
import random
from model.station import Station, StationReview
from model.user import User
from database.database import session, read_session

from log.log import logger
from sqlalchemy.sql import text


class Repository:
    def __init__(self):
        self.session = session
        self.read_session = read_session

    def get_users(self):
        try:
            # _offset = random.randint(15, 30000)
            _limit = random.randint(10, 1000)
            users = (
                self.read_session.query(User)
                .filter(User.is_enabled == True)
                .order_by(User.id.desc())
                # .offset(_offset)
                .limit(_limit)
                .all()
            )
            return users
        except Exception as e:
            logger.error(f"get_users e : {e}")

    def get_station_review_users(self):
        try:
            station_review_users = (
                self.read_session.query(User, StationReview)
                .join(StationReview, User.id == StationReview.user_id)
                .order_by(StationReview.id.desc())
                .limit(1000)
                .all()
            )
            return station_review_users
        except Exception as e:
            logger.error(f"get_station_review_users e : {e}")

    def get_stations(self):
        # _offset = random.randint(1, 1000)
        _limit = random.randint(10, 1000)
        stations = (
            self.read_session.query(Station)
            .join(StationReview, Station.id == StationReview.stat_id)
            # .offset(_offset)
            .limit(_limit)
            .all()
        )

        return stations

    def create_everycard(self):
        # create 할 때는 primary rds 에서 처리
        try:
            query = text(
                "insert into everycard (card_number, uid, is_used, is_lost, design_type) values (:card_number, :uid, :is_used, :is_lost, :design_type);"
            )

            params = {
                "card_number": str(uuid4()),
                "uid": str(uuid4()),
                "is_used": 0,
                "is_lost": 0,
                "design_type": "1",
            }

            session.execute(query, params)
            session.commit()
            logger.debug("create_everycard end")
        except Exception as e:
            logger.error(f"create_everycard e : {e}")
            return False

    def get_everycard(self):
        # get 할 때는 replica rds 에서 처리
        try:
            logger.debug("execute 실행")
            query = text("select * from everycard limit 10;")

            result = self.read_session.execute(query)
            logger.debug(f"get_everycard result : {result.fetchall()}")

            logger.debug("cursor.execute 실행")
        except Exception as e:
            logger.error(f"get_everycard e : {e}")
            return False
