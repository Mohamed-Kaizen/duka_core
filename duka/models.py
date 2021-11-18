"""Collection of pydantic model."""
from typing import Dict, Optional

import phonenumbers
from pydantic import BaseModel, EmailStr, Field, validator


class SessionVariables(BaseModel):
    """Schema for session variables data."""

    x_hasura_role: str = Field(None, alias="x-hasura-role")


class HasuraAction(BaseModel):
    """Schema for hasura action data."""

    name: str


class HasuraData(BaseModel):
    """Schema for hasura data data."""

    session_variables: SessionVariables

    action: HasuraAction


class HasuraEventDate(BaseModel):
    """Schema for hasura event data."""

    old: Optional[Dict]

    new: Dict


class HasuraEvent(BaseModel):
    """Schema for hasura event data."""

    session_variables: SessionVariables

    data: HasuraEventDate


class HasuraEventTrigger(BaseModel):
    """Schema for hasura trigger event data."""

    event: HasuraEvent


class PythonGraphqlClientResponse(BaseModel):
    """Schema for python graphql client response."""

    data: Optional[dict]

    errors: Optional[list[dict]]


class Passenger(BaseModel):
    """Schema for passenger."""

    first_name: str

    last_name: str

    email: EmailStr = ""

    phone_number: str

    gender: str

    @validator("phone_number")
    def extra_validation_on_phone_number(
        cls: "Passenger", value: str  # noqa B902
    ) -> str:
        """Extra Validation for the phone number.

        Args:
            cls: It the same as self # noqa: DAR102
            value: The phone number value from an input.

        Returns:
            The phone number if it is valid.

        Raises:
            ValueError: If phone_number is invalid it return 422 status.
        """
        try:
            phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(
                phone_number
            ) or not phonenumbers.is_possible_number(phone_number):
                raise ValueError("Invalid phone number")

        except Exception as error:
            raise ValueError(error) from error

        return value


class CreateTicketData(BaseModel):
    """Schema for ticket creation data."""

    trip_bus: str

    trip_bus_seat: list[str]

    passengers: list[Passenger]

    payment_method: str

    @validator("passengers")
    def match_passengers_seats(
        cls: "CreateTicketData", value: str, values: Dict[str, str]  # noqa B902
    ) -> str:
        """Checking if the passengers and trip_bus_seat length are equal."""
        if len(value) != len(values["trip_bus_seat"]):
            raise ValueError(
                f"passengers and seats are not matched,"
                f" passengers is {len(value)} and"
                f" seats are {len(values['trip_bus_seat'])}"
            )
        return value


class CreateTicketInput(BaseModel):
    """Schema for ticket creation input."""

    data: CreateTicketData


class CreateTicket(HasuraData):
    """Schema for ticket creation."""

    input: CreateTicketInput


class RouteInfo(BaseModel):
    """Schema for route info."""

    price: float


class TripInfo(BaseModel):
    """Schema for trip info."""

    route_info: RouteInfo


class TripBus(BaseModel):
    """Schema for trip bus."""

    bus: str

    trip: str

    status: str

    trip_info: TripInfo


class TripBusSeatInfo(BaseModel):
    """Schema for trip bus seat info."""

    name: str


class TripBusSeat(BaseModel):
    """Schema for trip bus seat."""

    id: str

    seat_info: TripBusSeatInfo

    status: str
