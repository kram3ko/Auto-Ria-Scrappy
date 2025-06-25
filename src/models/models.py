from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ParseCarModel(Base):
    __tablename__ = "parse_car"
    __table_args__ = (UniqueConstraint("car_number", "url", name="uq_car_number_url"),)

    url: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    price_usd: Mapped[int] = mapped_column(Integer)
    odometer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str] = mapped_column(String(65))
    phone_number: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    image_url: Mapped[str] = mapped_column(String(255))
    images_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    car_number: Mapped[str] = mapped_column(String(255))
    car_vin: Mapped[str] = mapped_column(String(255), unique=False)
    datetime_found: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), nullable=False)
