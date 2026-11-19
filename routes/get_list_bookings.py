import logging.config
from datetime import date
from typing import Optional

from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, Query, status
from schemas import BookingCreateOut
from services import get_all_bookings
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

router = APIRouter()


@router.get(
    "/bookings",
    response_model=list[BookingCreateOut],
    status_code=status.HTTP_200_OK,
)
async def get_bookings(
    date: Optional[date] = Query(
        default=None,
        description="Фильтр по дате (YYYY-MM-DD)",
        examples=["2026-12-15"],
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает список бронирований.

    Args:
        date (Optional[date]): Необязательная дата фильтрации.
            Если передана, возвращаются брони только на эту дату.
            Если не передана, возвращаются все брони.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия, получаемая через Depends(get_db).

    Returns:
        list[BookingCreateOut]: Список бронирований в формате BookingCreateOut.
            Если бронирований нет, возвращается пустой список [].

    Raises:
        HTTPException:
            Исключения обрабатываются на уровне сервисной функции <get_all_bookings>.
    """
    main_log.debug(
        "Начало обработки GET /bookings с параметром booking_date=%s",
        date,
    )
    main_log.info(
        "Запрос списка бронирований, фильтр по дате=%s",
        date,
    )

    result_get_bookings = await get_all_bookings(booking_date=date, db=db)

    if not result_get_bookings:
        main_log.info(
            "Бронирования не найдены для booking_date=%s",
            date,
        )
        return []

    return [
        BookingCreateOut(
            id=booking.id,
            name=person.name,
            phone=person.phone,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            guests=booking.guests,
            status=booking.status,
        )
        for booking, person in result_get_bookings
    ]
