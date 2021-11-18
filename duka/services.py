"""Collection of services."""
from typing import Any, Optional

from fastapi import HTTPException
from python_graphql_client import GraphqlClient

from .models import Passenger, PythonGraphqlClientResponse, TripBus, TripBusSeat
from .schema import (
    CREATE_PASSENGER,
    CREATE_PAYMENT_HISTORY,
    CREATE_SEATS,
    CREATE_TICKET_BY_CUSTOMER,
    CREATE_TICKET_BY_OPERATOR,
    CREATE_TICKET_BY_TICKETER,
    CREATE_TRIP_BUS_SEATS,
    CREATE_TRIP_HISTORY,
    GET_BUS,
    GET_TRIP_BUS,
    GET_TRIP_BUS_SEAT,
    UPDATE_TRIP_BUS_SEAT,
)
from .settings import SETTINGS
from .utils import random_string


async def graphql(
    *,
    query: str,
    variables: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> PythonGraphqlClientResponse:
    """Execute a graphql query."""
    if headers is None:
        headers = {"x-hasura-admin-secret": SETTINGS.HASURA_GRAPHQL_ADMIN_SECRET}

    client = GraphqlClient(endpoint=SETTINGS.HASURA_ENDPOINT_URL, headers=headers)

    resp = await client.execute_async(query=query, variables=variables)
    # print(resp)
    # print("%" * 100)
    return PythonGraphqlClientResponse(**resp)


async def add_seats(*, bus_id: str, seat_no: int) -> tuple[bool, Any]:
    """Add seats to an bus."""
    seats = [{"bus": bus_id, "name": f"{i}"} for i in range(1, seat_no)]

    resp = await graphql(query=CREATE_SEATS, variables={"objects": seats})

    if resp.errors:
        return False, resp.errors

    return True, f"{seat_no} has been added for bus_id: {bus_id}"


async def add_trip_history(
    *, bus_id: str, driver_id: str, trip_id: str
) -> tuple[bool, Any]:
    """Add trip history."""
    resp = await graphql(
        query=CREATE_TRIP_HISTORY,
        variables={"bus": bus_id, "driver": driver_id, "trip": trip_id},
    )

    if resp.errors:
        return False, resp.errors

    return True, "Trip History has been created."


async def get_bus(*, bus_id: str) -> tuple[bool, Any]:
    """Get bus info."""
    resp = await graphql(
        query=GET_BUS,
        variables={"id": bus_id},
    )

    if resp.errors:
        return False, resp.errors

    return True, resp.data


async def add_trip_bus_seat(*, trip_bus_id: str, seats: list[dict]) -> tuple[bool, Any]:
    """Add trip bus seats."""
    trip_bus_seats = [
        {
            "trip_bus": trip_bus_id,
            "status": "Available",
            "seat": f"{seat.get('id')}",
        }
        for seat in seats
    ]

    resp = await graphql(
        query=CREATE_TRIP_BUS_SEATS, variables={"objects": trip_bus_seats}
    )

    if resp.errors:
        return False, resp.errors

    return True, f"Seats has been added for trip_bus_id: {trip_bus_id}"


async def get_trip_bus(*, trip_bus_id: str) -> TripBus:
    """Get trip bus."""
    resp = await graphql(query=GET_TRIP_BUS, variables={"id": trip_bus_id})

    if resp.data:
        return TripBus(**resp.data.get("trip_bus_by_pk"))


async def is_seat_available(*, trip_bus_seats: list[str]) -> list[TripBusSeat]:
    """Get trip bus seat."""
    unavailable_seats = []

    available_seats = []

    for trip_bus_seat_id in trip_bus_seats:
        resp = await graphql(
            query=GET_TRIP_BUS_SEAT, variables={"id": trip_bus_seat_id}
        )

        try:
            if resp.data:
                trip_bus_seat = TripBusSeat(**resp.data.get("trip_bus_seat_by_pk"))

                if trip_bus_seat.status != "Available":
                    unavailable_seats.append(trip_bus_seat.seat_info.name)

                else:
                    available_seats.append(trip_bus_seat)

        except Exception as err:
            raise HTTPException(
                status_code=400,
                detail=f"There is no trip_bus_seat_id: {trip_bus_seat_id}",
            ) from err

    if unavailable_seats:
        raise HTTPException(
            status_code=400, detail=f"The seat: {unavailable_seats} cant be booked"
        )

    else:
        return available_seats


async def add_ticket(
    *,
    bus_id: str,
    trip_id: str,
    seats: list[TripBusSeat],
    price: float,
    passengers: list[Passenger],
    user_role: str,
    user_id: str,
    payment_method: str,
) -> None:
    """Add ticket."""
    create_ticket_mutation = CREATE_TICKET_BY_CUSTOMER

    variables = {
        "bus": bus_id,
        "code": random_string(),
        "customer": user_id,
        "trip": trip_id,
        "status": "Pendding",
    }

    if user_role == "operator":
        create_ticket_mutation = CREATE_TICKET_BY_OPERATOR

        variables = {
            "bus": bus_id,
            "operator": user_id,
            "trip": trip_id,
            "status": "Pendding",
        }

    elif user_role == "ticketer":
        create_ticket_mutation = CREATE_TICKET_BY_TICKETER
        variables = {
            "bus": bus_id,
            "ticketer": user_id,
            "trip": trip_id,
            "status": "Pendding",
        }
    for index, seat in enumerate(seats):

        variables.update({"seat": seat.id, "code": random_string()})

        resp = await graphql(query=create_ticket_mutation, variables=variables)

        ticket_id = resp.data.get("insert_ticket_one").get("id")

        passenger = passengers[index]

        await graphql(
            query=CREATE_PASSENGER,
            variables={
                "first_name": passenger.first_name,
                "last_name": passenger.last_name,
                "phone_number": passenger.phone_number,
                "gender": passenger.gender,
                "email": passenger.email,
                "ticket": ticket_id,
            },
        )

        await graphql(
            query=CREATE_PAYMENT_HISTORY,
            variables={
                "total_price": price,
                "system_price": 10,
                "method": payment_method,
                "ticket": ticket_id,
            },
        )

        await graphql(
            query=UPDATE_TRIP_BUS_SEAT,
            variables={
                "id": seat.id,
                "status": "Selected",
            },
        )
