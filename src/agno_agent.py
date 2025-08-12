from agno.agent import Agent, RunResponse
from agno.models.anthropic import Claude
from agno.agent import Agent, RunResponse  # noqa
from textwrap import dedent
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.logger import get_default_logger
from src.json_schema import InputResponse, FlightQueryData, FlightResponse

# Setup logger
logger = get_default_logger(__name__)


current_date_str = datetime.now().strftime("%Y-%m-%d")
logger.info(f"Initializing agno_agent with current date: {current_date_str}")

load_dotenv()

LLM_KEY = os.getenv("ANTHROPIC_API_KEY")
if LLM_KEY:
    logger.info("ANTHROPIC_API_KEY loaded successfully")
else:
    logger.warning("ANTHROPIC_API_KEY not found in environment variables")


def information_checker_agent():
    logger.info("Creating information_checker_agent")
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
    logger.info("information_checker_agent created successfully with agent_id: input-analyzer-agent")
    return information_checker_agent

def user_query_extractor_agent():
    # Agent that uses JSON mode
    logger.info("Creating user_query_extractor_agent")
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
    logger.info("user_query_extractor_agent created successfully with current date reference: {current_date_str}")
    return user_query_extractor

def init_flight_analyzer_agent():
    # Agent that uses JSON mode
    logger.info("Creating flight_list_analyzer_agent")
    flight_list_analyzer_agent = Agent(
        model=Claude(id="claude-3-5-sonnet-20240620"),
        description=dedent("""\
            You are a flight data analyzer. Your task is to review a JSON list in `flight_info` 
            containing multiple flights for multiple dates. Your goal is to identify the 
            overall top 10 flight options based on a balanced consideration of:

            1. **Price** – Lower is better.
            2. **Total travel time (duration)** – Shorter is better.
            3. **Number of stops** – Fewer stops are preferred, with non-stop flights 
            getting the highest preference unless the price difference is very large.

            Selection rules:
            - Always prioritize flights marked `best=True` if they meet the above criteria.
            - When comparing similar prices, prefer shorter travel time and fewer stops.
            - If two flights are nearly identical, prefer earlier departure times.
            - The list must contain flights across all dates in the data, not just a single date.
            - Include the top 10 flights overall, ranked best to least-best.
        """),
        instructions=dedent("""\
            Output must be valid JSON following the `FlightResponse` model.
            For each selected flight, include all original data plus:
                - `origin_airport` (same as `from_airport`)
                - `destination_airport` (same as `to_airport`)
            Do not include more than 10 flights in the final output.
            Ensure the list is sorted from best to least-best according to:
                1. Price (lowest first)
                2. Duration (shortest first)
                3. Stops (fewest first)
        """),
        response_model = FlightResponse,
        use_json_mode=True,
    )
    logger.info("flight_list_analyzer_agent created successfully")
    return flight_list_analyzer_agent




if __name__ == "__main__":
    logger.info("Starting main execution of agno_agent")
    
    try:
        # with open('flights.json', 'r') as fp:
        #     data = json.load(fp)
        # logger.info("Successfully loaded flights.json data")
        # data_str = json.dumps(data)
        # logger.info(f"Current date string: {current_date_str}")

        logger.info("Creating and running user_query_extractor_agent")
        query_extractor_agent = user_query_extractor_agent()
        json_mode_response: RunResponse = query_extractor_agent.run("Find me best flight for june from Bangalore to ahmedabad, preffered is indigo and air asia")
        
        logger.info("Query extractor agent response received successfully")
        logger.info(f"Extracted from_airport: {json_mode_response.content.from_airport}")
        logger.info(f"Full response content: {json_mode_response.content}")

        # flight_list_analyzer_agent = init_flight_analyzer_agent()
        # json_mode_response: RunResponse = flight_list_analyzer_agent.run(data_str)
        print(json_mode_response.content, json_mode_response.content.from_airport)
        
        logger.info("Main execution completed successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")
        print(f"Unexpected error: {e}")

# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)