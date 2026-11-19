import logging.config

from core import dict_config
from fastapi import FastAPI
from routes import (
    route_create_booking,
    route_delete_by_id,
    route_get_bookings_by_id,
    route_get_list_bookings,
)

logging.config.dictConfig(dict_config)

app = FastAPI(
    title="Restaurant Booking API",
    description="REST API для бронирования столиков в ресторане.",
    version="1.0.0",
)

app.include_router(route_create_booking, tags=["Bookings"])
app.include_router(route_get_list_bookings, tags=["Bookings"])
app.include_router(route_get_bookings_by_id, tags=["Bookings"])
app.include_router(route_delete_by_id, tags=["Bookings"])
