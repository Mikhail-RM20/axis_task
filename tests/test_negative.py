from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_double_booking_conflict_409(client: AsyncClient):
    """1. Повторная бронь на уже занятый активный слот возвращает 409."""
    target_date = (date.today() + timedelta(days=7)).isoformat()
    payload = {
        "name": "Игорь",
        "phone": "+79990001122",
        "booking_date": target_date,
        "booking_time": "17:00:00",
        "guests": 4,
    }

    first_resp = await client.post("/bookings", json=payload)
    assert first_resp.status_code == 201

    second_resp = await client.post("/bookings", json=payload)
    assert second_resp.status_code == 409
    assert second_resp.json() == {"detail": "Slot is already booked"}


@pytest.mark.asyncio
async def test_booking_not_found_404(client: AsyncClient):
    """2. Получение или отмена несуществующей брони возвращает 404."""
    get_resp = await client.get("/bookings/99999")
    assert get_resp.status_code == 404
    assert get_resp.json() == {"detail": "Booking not found"}

    delete_resp = await client.delete("/bookings/99999")
    assert delete_resp.status_code == 404
    assert delete_resp.json() == {"detail": "Booking not found"}


@pytest.mark.asyncio
async def test_invalid_date_and_time_422(client: AsyncClient):
    """3. Дата в прошлом / дальше 30 дней и нецелый час или вне 12:00-22:00 дают 422."""
    past_date = (date.today() - timedelta(days=1)).isoformat()
    far_future_date = (date.today() + timedelta(days=31)).isoformat()
    valid_date = (date.today() + timedelta(days=2)).isoformat()

    resp_past = await client.post(
        "/bookings",
        json={
            "name": "Тест",
            "phone": "+79991234567",
            "booking_date": past_date,
            "booking_time": "15:00:00",
            "guests": 2,
        },
    )
    assert resp_past.status_code == 422

    resp_far = await client.post(
        "/bookings",
        json={
            "name": "Тест",
            "phone": "+79991234567",
            "booking_date": far_future_date,
            "booking_time": "15:00:00",
            "guests": 2,
        },
    )
    assert resp_far.status_code == 422

    resp_half_hour = await client.post(
        "/bookings",
        json={
            "name": "Тест",
            "phone": "+79991234567",
            "booking_date": valid_date,
            "booking_time": "15:30:00",
            "guests": 2,
        },
    )
    assert resp_half_hour.status_code == 422

    resp_late = await client.post(
        "/bookings",
        json={
            "name": "Тест",
            "phone": "+79991234567",
            "booking_date": valid_date,
            "booking_time": "23:00:00",
            "guests": 2,
        },
    )
    assert resp_late.status_code == 422


@pytest.mark.asyncio
async def test_invalid_phone_name_and_guests_422(client: AsyncClient):
    """4. Неверный формат телефона, длина имени и количество гостей дают 422."""
    valid_date = (date.today() + timedelta(days=2)).isoformat()

    resp_phone = await client.post(
        "/bookings",
        json={
            "name": "Тест",
            "phone": "89991234567",
            "booking_date": valid_date,
            "booking_time": "16:00:00",
            "guests": 2,
        },
    )
    assert resp_phone.status_code == 422

    resp_name_guests = await client.post(
        "/bookings",
        json={
            "name": "А",
            "phone": "+79991234567",
            "booking_date": valid_date,
            "booking_time": "16:00:00",
            "guests": 11,
        },
    )
    assert resp_name_guests.status_code == 422