"""Collection of graphql schema."""
CREATE_SEATS = """
mutation CreateSeats($objects: [seat_insert_input!]!) {
  insert_seat(objects: $objects) {
    affected_rows
  }
}
"""


CREATE_TRIP_HISTORY = """
mutation CreateTripHistory($bus: uuid!, $driver: uuid!, $trip: uuid!) {
  insert_trip_history_one(object: {bus: $bus, driver: $driver, trip: $trip}) {
    id
  }
}
"""


GET_BUS = """
query GetBus($id: uuid!) {
  bus_by_pk(id: $id) {
    id
    driver
    seats {
      id
    }
  }
}
"""


CREATE_TRIP_BUS_SEATS = """
mutation CreateTripBusSeat($objects: [trip_bus_seat_insert_input!]!) {
  insert_trip_bus_seat(objects: $objects) {
    affected_rows
  }
}
"""

GET_TRIP_BUS = """
query GetTripBus($id: uuid!) {
  trip_bus_by_pk(id: $id) {
    bus
    trip
    status
    trip_info {
      route_info {
        price
      }
    }
  }
}
"""


GET_TRIP_BUS_SEAT = """
query GetTripBusSeat($id: uuid!) {
  trip_bus_seat_by_pk(id: $id) {
    id
    seat_info {
      name
    }
    status
  }
}
"""


CREATE_TICKET_BY_CUSTOMER = """
mutation CreateTicketByCustomer($bus: uuid!, $code: String!, $customer: uuid!, $seat: uuid!, $trip: uuid!, $status: ticket_status_enum!) {
  insert_ticket_one(object: {code: $code, bus: $bus, trip: $trip, seat: $seat, customer: $customer, status: $status}) {
    id
  }
}
"""


CREATE_TICKET_BY_OPERATOR = """
mutation CreateTicketByOperator($bus: uuid!, $code: String!, $operator: uuid!, $seat: uuid!, $trip: uuid!, $status: ticket_status_enum!) {
  insert_ticket_one(object: {code: $code, bus: $bus, trip: $trip, seat: $seat, operator: $operator, status: $status}) {
    id
  }
}
"""


CREATE_TICKET_BY_TICKETER = """
mutation CreateTicketByTicketer($bus: uuid!, $code: String!, $ticketer: uuid!, $seat: uuid!, $trip: uuid!, $status: ticket_status_enum!) {
  insert_ticket_one(object: {code: $code, bus: $bus, trip: $trip, seat: $seat, ticketer: $ticketer, status: $status}) {
    id
  }
}
"""


CREATE_PASSENGER = """
mutation CreatePassenger($first_name: String!, $last_name: String!, $phone_number: String!, $gender: users_gender_enum!, $email: String!, $ticket: uuid!) {
  insert_passenger_one(object: {first_name: $first_name, last_name: $last_name, phone_number: $phone_number, gender: $gender, email: $email, ticket: $ticket}) {
    id
  }
}
"""


CREATE_PAYMENT_HISTORY = """
mutation CreatePaymentHistory($ticket: uuid!, $total_price: numeric!, $system_price: numeric!, $method: payment_method_enum!) {
  insert_payment_history_one(object: {ticket: $ticket, total_price: $total_price, system_price: $system_price, method: $method}) {
    id
  }
}
"""

UPDATE_TRIP_BUS_SEAT = """
mutation UpdateTripBusSeat($id: uuid!, $status: seat_status_enum!) {
  update_trip_bus_seat_by_pk(pk_columns: {id: $id}, _set: {status: $status}) {
    id
    status
  }
}
"""
