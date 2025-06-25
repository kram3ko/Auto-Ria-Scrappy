from datetime import datetime

from sqlalchemy import String, Integer, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ParseCarModel(Base):
    __tablename__ = "parse_car"
    __table_args__ = (
        UniqueConstraint("car_number", "url", name="uq_car_number_url"),
    )

    url: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    price_usd: Mapped[int] = mapped_column(Integer)
    odometer: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String(65))
    phone_number: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String(255))
    images_count: Mapped[int] = mapped_column(Integer)
    car_number: Mapped[str] = mapped_column(String(255))
    car_vin: Mapped[str] = mapped_column(String(255), unique=False)
    datetime_found: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != "id"}
