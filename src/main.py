from agno.agent import Agent, RunResponse
from agno.agent import Agent, RunResponse  # noqa
from typing import List
import json
from src.agno_agent import FlightQueryData, user_query_extractor_agent, init_flight_analyzer_agent, information_checker_agent
from src.core import process_date, search_flights_parallel
from src.logger import get_default_logger
import certifi
import os
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Setup logger
logger = get_default_logger(__name__)

class FlightAgent:
    def __init__(self) -> None:
        self.query_extractor_agent = user_query_extractor_agent()
        logger.info("Creating and running user query extractor agent")
        self.flight_list_analyzer_agent = init_flight_analyzer_agent()
        logger.info("Creating and running flight list analyzer agent")
    
    def search_flights(self, user_query):
        logger.info(f"Starting flight search for query: {user_query}")
        
        #Note:: Added the information checker first, not needed for frontend integration
        # input_supervisor = information_checker_agent()
        # input_response: RunResponse = input_supervisor.run(user_query)
        # logger.debug(f"Input response: {input_response}")
        # input_json_response = input_response.content.model_dump()
        # logger.debug(f"Input JSON response: {input_json_response['to_send_next_agent']}, type: {type(input_json_response['to_send_next_agent'])}")
        
        if True: #input_json_response['to_send_next_agent'] == True:
            
            json_mode_response: RunResponse = self.query_extractor_agent.run(user_query)
            user_filters = json_mode_response.content

            user_filters_json = user_filters.model_dump(mode='json')
            logger.info(f"User filters extracted: {user_filters_json}")
            
            logger.info("Starting parallel flight search")
            all_flights_results = search_flights_parallel(user_filters_json)
            logger.info("Flight search completed")
            logger.debug(f"Flight search results: {all_flights_results}")

            all_flights_results_str = json.dumps(all_flights_results)
            # with open('flights.json', 'w') as fp:
            #     json.dump(all_flights_results, fp)

            
            best_flight_result: RunResponse = self.flight_list_analyzer_agent.run(all_flights_results_str)
            best_flight_result = best_flight_result.content.model_dump()
            logger.info("Flight analysis completed")
            logger.debug(f"Best flight result: {best_flight_result}")
            
            #Adding a redirect URL
            logger.info("Adding redirect URLs to flight results")
            for each_results in best_flight_result['flight_search_results']:
                redirect_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{each_results['destination_airport']}%20from%20{each_results['origin_airport']}%20on%20{each_results['Date']}%20one%20way%20economy%20class&curr=INR"
                each_results['redirect_url'] = redirect_url
                logger.debug(f"Added redirect URL for flight: {each_results['origin_airport']} to {each_results['destination_airport']}")
            
            logger.info("Flight search and analysis completed successfully")
            logger.debug(f"Final flight result: {best_flight_result}")
                
        else:
            logger.warning("Input validation failed, returning user message")
            best_flight_result = input_json_response['ask_user_message']
        
        logger.info("Flight search function completed")
        logger.info(f"Best flight result: {best_flight_result}")
        return best_flight_result


if __name__ == "__main__":
    logger.info("Starting main.py execution")
    flight_agent = FlightAgent()
    user_query = "Hi, Looking for Bangalore to Vadodara for 1 adult on 27th May 2025"
    
    try:
        best_flight_result = flight_agent.search_flights(user_query)
        logger.info("Main execution completed successfully")
        # logger.debug(f"Final result: {best_flight_result}")
        
    except Exception as e:
        logger.error(f"Error during main execution: {e}")
        raise
