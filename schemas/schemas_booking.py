from datetime import date, time, timedelta

from database import BookingStatus
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

BOOKING_TIMES = {
    time(12, 0),
    time(13, 0),
    time(14, 0),
    time(15, 0),
    time(16, 0),
    time(17, 0),
    time(18, 0),
    time(19, 0),
    time(20, 0),
    time(21, 0),
    time(22, 0),
}


class BookingCreateIn(BaseModel):
    name: str = Field(
        ...,
        title="Имя человека.",
        examples=["Максим"],
        min_length=2,
        max_length=50,
    )
    phone: str = Field(
        ...,
        title="Номер телефона человека.",
        description="Номер телефона в формате +7XXXXXXXXXX (ровно 10 цифр после +7).",
        examples=["+79991234567"],
        pattern=r"^\+7\d{10}$",
    )
    booking_date: date = Field(
        ...,
        title="Дата бронирования.",
    )
    booking_time: time = Field(
        ...,
        title="Время бронирования.",
        description="Только целые часы с 12:00 до 22:00.",
    )
    guests: int = Field(
        ...,
        title="Кол-во гостей.",
        description="Кол-во персон от 1 до 10.",
        ge=1,
        le=10,
    )

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        today = date.today()
        max_date = today + timedelta(days=30)
        if v < today:
            raise ValueError("Дата бронирования не может быть в прошлом.")
        if v > max_date:
            raise ValueError(
                "Дата бронирования не может быть дальше чем через 30 дней."
            )
        return v

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, v: time) -> time:
        if v not in BOOKING_TIMES:
            raise ValueError(
                "Время бронирования должно быть целым часом с 12:00 до 22:00."
            )
        return v


class BookingCreateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int = Field(
        ...,
        title="ID-брони.",
        description="ID созданного бронирования.",
    )
    name: str = Field(..., title="Имя человека.")
    phone: str = Field(..., title="Номер телефона человека.")
    booking_date: date = Field(..., title="Дата бронирования.")
    booking_time: time = Field(..., title="Время бронирования.")
    guests: int = Field(..., title="Кол-во гостей.")
    status: BookingStatus = Field(
        ...,
        title="Статус брони.",
    )
