import logging

from database import Booking, BookingStatus, Person
from fastapi import HTTPException, status
from schemas import BookingCreateIn
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

main_log = logging.getLogger("services_logger")


async def create_new_booking(
    information_booking: BookingCreateIn, db: AsyncSession
) -> tuple[Booking, Person]:
    """
    Создаёт нового человека и новую бронь в базе данных.

    Args:
        information_booking (BookingCreateIn): Данные для создания бронирования.
            Ожидаются поля name, phone, booking_date, booking_time, guests.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия.

    Returns:
        tuple[Booking, Person]: Кортеж из созданной брони и связанного человека.
            Сначала возвращается объект Booking, затем объект Person.

    Raises:
        HTTPException:
            409 — если слот уже занят или произошла ошибка целостности данных.
            500 — при любой другой ошибке базы данных.
    """
    main_log.debug("Начало создания новой брони")
    main_log.info(
        "Получены данные на создание брони: name=%s, phone=%s, booking_date=%s, booking_time=%s, guests=%s",
        information_booking.name,
        information_booking.phone,
        information_booking.booking_date,
        information_booking.booking_time,
        information_booking.guests,
    )

    try:
        stmt = select(Booking).where(
            Booking.booking_date == information_booking.booking_date,
            Booking.booking_time == information_booking.booking_time,
            Booking.status == BookingStatus.active,
        )
        result = await db.execute(stmt)
        existing_booking = result.scalars().first()

        if existing_booking:
            main_log.info(
                "Попытка создать дубликат брони: booking_date=%s, booking_time=%s",
                information_booking.booking_date,
                information_booking.booking_time,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot is already booked",
            )

        person = Person(
            name=information_booking.name,
            phone=information_booking.phone,
        )
        db.add(person)
        await db.flush()

        main_log.info(
            "Создан объект Person: person_id=%s, name=%s",
            person.id,
            person.name,
        )

        booking = Booking(
            person_id=person.id,
            booking_date=information_booking.booking_date,
            booking_time=information_booking.booking_time,
            guests=information_booking.guests,
            status=BookingStatus.active,
        )
        db.add(booking)

        await db.commit()
        await db.refresh(booking)
        await db.refresh(person)

        main_log.info(
            "Бронь успешно создана: booking_id=%s, person_id=%s",
            booking.id,
            person.id,
        )

        return booking, person

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError as e:
        main_log.exception(
            "Ошибка целостности данных при создании брони: %s", e
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot is already booked",
        )

    except SQLAlchemyError as e:
        main_log.exception("Ошибка БД при создании брони: %s", e)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )
