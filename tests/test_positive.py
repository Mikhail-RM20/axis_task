from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_booking_by_id(client: AsyncClient):
    """1. Успешное создание брони (201) и получение её по ID (200)."""
    target_date = (date.today() + timedelta(days=2)).isoformat()
    payload = {
        "name": "Максим",
        "phone": "+79991234567",
        "booking_date": target_date,
        "booking_time": "19:00:00",
        "guests": 4,
    }

    create_resp = await client.post("/bookings", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "Максим"
    assert created["phone"] == "+79991234567"
    assert created["booking_date"] == target_date
    assert created["booking_time"] == "19:00:00"
    assert created["guests"] == 4
    assert created["status"] == "active"

    get_resp = await client.get(f"/bookings/{created['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json() == created


@pytest.mark.asyncio
async def test_get_bookings_list_and_date_filter(client: AsyncClient):
    """2. Получение списка броней и фильтрация по параметру ?date= (200)."""
    date_first = (date.today() + timedelta(days=3)).isoformat()
    date_second = (date.today() + timedelta(days=4)).isoformat()

    await client.post(
        "/bookings",
        json={
            "name": "Анна",
            "phone": "+79991112233",
            "booking_date": date_first,
            "booking_time": "14:00:00",
            "guests": 2,
        },
    )
    await client.post(
        "/bookings",
        json={
            "name": "Олег",
            "phone": "+79994445566",
            "booking_date": date_second,
            "booking_time": "18:00:00",
            "guests": 5,
        },
    )

    all_resp = await client.get("/bookings")
    assert all_resp.status_code == 200
    assert len(all_resp.json()) == 2

    filtered_resp = await client.get(f"/bookings?date={date_first}")
    assert filtered_resp.status_code == 200
    filtered_data = filtered_resp.json()
    assert len(filtered_data) == 1
    assert filtered_data[0]["name"] == "Анна"
    assert filtered_data[0]["booking_date"] == date_first


@pytest.mark.asyncio
async def test_cancel_booking_keeps_record(client: AsyncClient):
    """3. Отмена брони меняет статус на cancelled без удаления записи из БД (200)."""
    target_date = (date.today() + timedelta(days=5)).isoformat()
    create_resp = await client.post(
        "/bookings",
        json={
            "name": "Елена",
            "phone": "+79997778899",
            "booking_date": target_date,
            "booking_time": "21:00:00",
            "guests": 2,
        },
    )
    booking_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/bookings/{booking_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "cancelled"

    get_resp = await client.get(f"/bookings/{booking_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_rebook_cancelled_slot(client: AsyncClient):
    """4. Отменённая бронь освобождает слот для повторного бронирования (201)."""
    target_date = (date.today() + timedelta(days=6)).isoformat()
    payload = {
        "name": "Дмитрий",
        "phone": "+79993332211",
        "booking_date": target_date,
        "booking_time": "20:00:00",
        "guests": 3,
    }

    first_resp = await client.post("/bookings", json=payload)
    booking_id = first_resp.json()["id"]

    await client.delete(f"/bookings/{booking_id}")

    second_resp = await client.post("/bookings", json=payload)
    assert second_resp.status_code == 201
    assert second_resp.json()["status"] == "active"
    assert second_resp.json()["id"] != booking_id