"""App for Duka File Uploader Project."""
import logging
import sys
from typing import Any, Union

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from .logger import InterceptHandler, log_format
from .models import CreateTicket, HasuraEventTrigger
from .services import (
    add_seats,
    add_ticket,
    add_trip_bus_seat,
    add_trip_history,
    get_bus,
    get_trip_bus,
    is_seat_available,
)
from .settings import REDIS, SETTINGS, EnvSettings

app = FastAPI(
    title=SETTINGS.PROJECT_NAME,
    description=SETTINGS.PROJECT_DESCRIPTION,
    version="0.1.0",
    docs_url=SETTINGS.DOCS_URL,
    redoc_url=SETTINGS.REDOC_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.CORS_ORIGINS,
    allow_credentials=SETTINGS.CORS_ALLOW_CREDENTIALS,
    allow_methods=SETTINGS.CORS_ALLOW_METHODS,
    allow_headers=SETTINGS.CORS_ALLOW_HEADERS,
)


@AuthJWT.load_config
def get_config() -> EnvSettings:
    """A callback to get your configuration."""
    return SETTINGS


@app.exception_handler(AuthJWTException)
def auth_exception_handler(request: Request, exc: AuthJWTException) -> ORJSONResponse:
    """Exception handler for authjwt."""
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@AuthJWT.token_in_denylist_loader
def check_if_token_in_deny_list(
    decrypted_token: dict[str, Any]
) -> Union[str, None, bool]:
    """Checking if the tokens jti is in the deny list set."""
    jti = decrypted_token["jti"]
    entry = REDIS.get(jti)
    return entry and entry == "true"


@app.post("/create-seat", response_class=ORJSONResponse)
async def create_seat(event_data: HasuraEventTrigger) -> Response:
    """Create seats for a bus."""
    created, message = await add_seats(
        bus_id=event_data.event.data.new.get("id"),
        seat_no=int(event_data.event.data.new.get("total_seat")) + 1,
    )

    if created:
        return Response(status_code=200, content=message)

    return Response(status_code=400, content=message)


@app.post("/create-trip-history", response_class=ORJSONResponse)
async def create_trip_history(event_data: HasuraEventTrigger) -> Response:
    """Create trip history."""
    bus_id = event_data.event.data.new.get("bus")

    _, data = await get_bus(bus_id=bus_id)

    created, message = await add_trip_history(
        bus_id=bus_id,
        driver_id=data.get("bus_by_pk").get("driver"),
        trip_id=event_data.event.data.new.get("trip"),
    )

    if created:
        return Response(status_code=200, content=message)

    return Response(status_code=400, content=message)


@app.post("/create-trip-bus-seat", response_class=ORJSONResponse)
async def create_trip_bus_seat(event_data: HasuraEventTrigger) -> Response:
    """Create seats for trip bus."""
    bus_id = event_data.event.data.new.get("bus")

    _, data = await get_bus(bus_id=bus_id)

    created, message = await add_trip_bus_seat(
        trip_bus_id=event_data.event.data.new.get("id"),
        seats=data.get("bus_by_pk").get("seats"),
    )

    if created:
        return Response(status_code=200, content=message)

    return Response(status_code=400, content=message)


@app.post("/create-ticket", response_class=ORJSONResponse)
async def create_ticket(
    user_input: CreateTicket,
    authorize: AuthJWT = Depends(),
) -> Response:
    """Create ticket for a trip."""
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()

    if user_input.session_variables.x_hasura_role == "admin":
        return Response(
            status_code=400, content='{"detail": "Sorry...you cant create a ticket :("}'
        )

    trip_bus_data = await get_trip_bus(trip_bus_id=user_input.input.data.trip_bus)

    trip_bus_seats = await is_seat_available(
        trip_bus_seats=user_input.input.data.trip_bus_seat
    )

    if user_input.input.data.payment_method in [
        "CBE_Branch",
        "CBE_Birr",
        "Cash",
        "Awash_Branch",
        "Nib_Branch",
        "Abyssinia_branch",
    ]:
        await add_ticket(
            bus_id=trip_bus_data.bus,
            trip_id=trip_bus_data.trip,
            user_id=user_id,
            seats=trip_bus_seats,
            price=trip_bus_data.trip_info.route_info.price,
            passengers=user_input.input.data.passengers,
            user_role=user_input.session_variables.x_hasura_role,
            payment_method=user_input.input.data.payment_method,
        )

    return Response(status_code=200, content='{"detail": "Ticket has been created"}')


logging.getLogger().handlers = [InterceptHandler()]
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "level": SETTINGS.LOG_LEVEL,
            "format": log_format,
        }
    ]
)
logger.add("logs/file_{time:YYYY-MM-DD}.log", level="TRACE", rotation="1 day")

logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
