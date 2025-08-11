import json
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timedelta

class FlightQueryData(BaseModel):
    from_airport: str = Field(
        ...,
        description="Airport code for the departure city (e.g., BLR for Bangalore, AMD for Ahmedabad). Required field that represents the starting point of the journey."
    )
    to_airport: str = Field(
        ...,
        description="Airport code for the destination city (e.g., BLR for Bangalore, AMD for Ahmedabad, MUC for Munich). Required field that represents the endpoint of the journey."
    )
    adults: int = Field(
        1,
        description="Number of adult passengers (age 12+) traveling. Defaults to 1 if not specified in the query."
    )
    children: int = Field(
        0,
        description="Number of children passengers (age 2-11) traveling. Defaults to 0 if not specified in the query."
    )
    infants_in_seat: int = Field(
        0,
        description="Number of infant passengers (under age 2) requiring their own seat. Defaults to 0 if not specified in the query."
    )
    infants_on_lap: int = Field(
        0,
        description="Number of infant passengers (under age 2) traveling on an adult's lap. Defaults to 0 if not specified in the query."
    )
    trip_type: str = Field(
        "one-way",
        description="Type of journey: 'one-way' (single direction) or 'round-trip' (return journey included). Defaults to 'one-way' if not specified."
    )
    seat: str = Field(
        "economy",
        description="Class of travel requested (e.g., economy, premium economy, business, first). Defaults to 'economy' if not specified."
    )
    date_list: List[str] = Field(
        ...,
        description="List of potential travel dates in 'yyyy-mm-dd' format. For date ranges, should include all dates within the range. Required field."
    )
    specific_flight_provider: List[str] = Field(
        [],
        description="List of preferred airlines or flight operators (e.g., IndiGo, Air India, Akasa Air). Empty list if no specific provider requested."
    )
    flight_time_type: List[str] = Field(
        [],
        description="Preferred time of day for flights (e.g., morning, afternoon, evening, night). Empty list if no time preference specified."
    )
    max_stops: int = Field(
        1,
        description="Maximum number of stops acceptable for the journey. Use 0 for non-stop/direct flights only. Defaults to 1 if not specified."
    )
    price_type: str = Field(
        "minimum",
        description="Price preference for flight selection (e.g., minimum, maximum, average). Defaults to 'minimum' to prioritize lowest-cost options."
    )
    travel_duration: str = Field(
        "less than 6 hours",
        description="Travel duration preference for flight selection (e.g., less than 6 hours, 6-12 hours, 12-24 hours, more than 24 hours). Defaults to 'less than 6 hours' to prioritize shorter travel times."
    )



class InputResponse(BaseModel):
    to_send_next_agent: bool = Field(
        ...,
        description="If all the necessary information related to flight search is given make this value True or else False",
    )
    ask_user_message: str = Field(
        ...,
        description="Ask neccesary question/response message to the user if the information is missing, add this question in this field",
    )
class FlightSearchResult(BaseModel):
    flight_vendor: str = Field(
        ...,
        description = "Name of the Flight Vendor i.e Indigo, Akasa Air etc"
    )
    departure: str = Field(
        ...,
        description = "Departure flight time"
    )
    arrival: str  = Field(
        ...,
        description = "Arrival flight time"
    )
    origin_airport: str = Field(
        ...,
        description = "IATA code for origin airport"
    )
    destination_airport: str = Field(
        ...,
        description = "IATA code for destination airport"
    )
    Date: str = Field(
        ...,
        description = "Flight date"
    )    # Consider using `date` or a `datetime.date` field
    stops: int = Field(
        ...,
        description = "No of Stops of the flight"
    )  
    price: str = Field(
        ...,
        description = "Price of the flight"
    )
    arrival_time_ahead: str = Field(
        ...,
        description = "Arrival time ahead of departure time"
    )
    duration: str = Field(
        ...,
        description = "Duration of the flight"
    )



class FlightResponse(BaseModel):
    flight_search_results: List[FlightSearchResult]


class FlightJSON:
    def __init__(self, is_best, name, departure, arrival, arrival_time_ahead, duration, stops, delay, price):
        self.is_best = is_best
        self.name = name
        self.departure = departure
        self.arrival = arrival
        self.arrival_time_ahead = arrival_time_ahead
        self.duration = duration
        self.stops = stops
        self.delay = delay
        self.price = price

    def to_dict(self):
        return {
            "is_best": self.is_best,
            "name": self.name,
            "departure": self.departure,
            "arrival": self.arrival,
            "arrival_time_ahead": self.arrival_time_ahead,
            "duration": self.duration,
            "stops": self.stops,
            "delay": self.delay,
            "price": self.price
        }

class Result:
    def __init__(self, current_price, flights):
        self.current_price = current_price
        self.flights = flights

    def to_dict(self):
        return {
            "current_price": self.current_price,
            "flights": [flight.to_dict() for flight in self.flights]
        }