from agno.agent import Agent, RunResponse
from agno.models.anthropic import Claude
from agno.agent import Agent, RunResponse  # noqa
from pydantic import BaseModel, Field
from textwrap import dedent
from typing import List
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


current_date_str = datetime.now().strftime("%Y-%m-%d")
load_dotenv()

LLM_KEY = os.getenv("ANTHROPIC_API_KEY")

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


class FlightResponse(BaseModel):
    flight_search_results: List[FlightSearchResult]



def information_checker_agent():
    information_checker_agent = Agent(
        agent_id="input-analyzer-agent",
        model=Claude(id="claude-3-5-sonnet-20240620"),
        description=dedent("""\
            You're a flight analyze superviser who checks the user input. Check the user's input if that contains, information
            regarding source and destination cities, also check for valid month, date or date range if user has provided. If not,
            ask necessary questions to gather information such as source city, destination city, timeline and number of adults.
        """),
        instructions=dedent("""\
        Give the output in JSON containing a boolean value and a response message.
            - Response should be either a question to the user or response about proceeding further if all information is provided.
            - Boolean value is meant to be True/False depending if all the flight search related info is provided.
            - If `to_send_next_agent` is True, then only give response like we're processing the information, wait for sometime or similar to this.
            - the dates could be a month like "July, June, 2025" or some specific from 15th June to 20th June date range.
            - User can give whole month for search, take that as a correct input.
        """),
        response_model=InputResponse,
        debug_mode=True,
        use_json_mode=True,
        add_history_to_messages=True,
    )
    return information_checker_agent

def user_query_extractor_agent():
    # Agent that uses JSON mode
    user_query_extractor = Agent(
        model=Claude(id="claude-3-5-sonnet-20240620"),
        description=dedent("""\
            Hi, you are a flight data related query extractor. 
             Your job is based on user's query, you need to fill up certain values in a dictionary.
            - If a user has given a date range such as from and to, then select all the dates between these two dates.
                     
        """),
        instructions=dedent("""\
        IMPORTANT: Always use today's date ({current_date_str}) as your reference point for all date calculations.
        While filling up the dictionary:
            - Keep the valid airport tags, if city does not have an airport, keep it None
            - Keep the date list in an increasing order.
            - By default keep seat economy.
            - Specify all the dates for a mentioned date range
        """),
        response_model=FlightQueryData,
        use_json_mode=True,
        add_datetime_to_instructions=True,
    )
    return user_query_extractor

def init_flight_analyzer_agent():
    # Agent that uses JSON mode
    flight_list_analyzer_agent = Agent(
        model=Claude(id="claude-3-5-sonnet-20240620"),
        description=dedent("""\
            You're a flight data analyzer whose task is to from a given list of data in `flight_info` which contains flight 
            information for dates, you need to select a particular date where the flight price is cheapest. 
            - While selecting the best deal, look after about the travel time, max stops, 
            give priority to non-stop flight if the prices are not too high, otherwise give the priority to other deals.
            - There could be multiple best deals, select best deals across all the flight data.             
        """),
        instructions=dedent("""\
        When selecting a flight, use this conditions:
            - select a flight which is more convienient, less travel time.
            - Select the flight which has a lesser price.
            - Also append from_airport as origin_airport and to_airport as destination_airport in the output JSON
        """),
        response_model = FlightResponse,
        use_json_mode=True,
    )
    return flight_list_analyzer_agent




if __name__ == "__main__":
    with open('flights.json', 'r') as fp:
        data = json.load(fp)
    data_str = json.dumps(data)
    print(current_date_str)

    query_extractor_agent = user_query_extractor_agent()
    json_mode_response: RunResponse = query_extractor_agent.run("Find me best flight for june from Bangalore to ahmedabad, preffered is indigo and air asia")

    # flight_list_analyzer_agent = init_flight_analyzer_agent()
    # json_mode_response: RunResponse = flight_list_analyzer_agent.run(data_str)
    print(json_mode_response.content, json_mode_response.content.from_airport)

# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)