import logging

from database import get_db
from fastapi import APIRouter, Depends, status
from schemas import BookingCreateOut
from services import get_booking_id
from sqlalchemy.ext.asyncio import AsyncSession

main_log = logging.getLogger("route_logger")

router = APIRouter()


@router.get(
    "/bookings/{id}",
    response_model=BookingCreateOut,
    status_code=status.HTTP_200_OK,
)
async def get_booking_table_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает данные брони по её ID.

    Args:
        id (int): ID брони, которую нужно получить.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия, получаемая через Depends(get_db).

    Returns:
        BookingCreateOut: Данные брони, включая:
            - id: ID брони
            - name: имя человека, к которому привязана бронь
            - phone: телефон человека
            - booking_date: дата бронирования
            - booking_time: время бронирования
            - guests: количество гостей
            - status: текущий статус брони

    Raises:
        HTTPException:
            Исключения обрабатываются на уровне сервисной функции <get_booking_id>.
    """
    main_log.debug("Начало обработки GET /bookings/%s", id)
    main_log.info("Запрос на получение брони по id=%s", id)

    booking, person = await get_booking_id(booking_id=id, db=db)

    main_log.info(
        "Бронь успешно найдена: booking_id=%s, person_id=%s, name=%s",
        booking.id,
        booking.person_id,
        person.name,
    )
    return BookingCreateOut.from_models(booking, person)
