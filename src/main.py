from agno.agent import Agent, RunResponse
from agno.agent import Agent, RunResponse  # noqa
from typing import List
import json
from src.agno_agent import FlightQueryData, user_query_extractor_agent, init_flight_analyzer_agent, information_checker_agent
from src.core import process_date, search_flights_parallel
import certifi
import os
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()



user_query = "Hi, Looking for Bangalore to Vadodara for 1 adult on 27th May 2025"
# user_query = "Hi, Can you search for Bangalore flights?"

def search_flights(user_query):
    # input_supervisor = information_checker_agent()
    # input_response: RunResponse = input_supervisor.run(user_query)
    # # print(input_response)
    # input_json_response = input_response.content.model_dump()
    # print(input_json_response['to_send_next_agent'], type(input_json_response['to_send_next_agent']))
    if True: #input_json_response['to_send_next_agent'] == True:
        query_extractor_agent = user_query_extractor_agent()
        json_mode_response: RunResponse = query_extractor_agent.run(user_query)
        user_filters = json_mode_response.content

        user_filters_json = user_filters.model_dump(mode='json')
        print(user_filters_json)
        all_flights_results = search_flights_parallel(user_filters_json)
        print("****"*10)
        print(all_flights_results)

        all_flights_results_str = json.dumps(all_flights_results)


        flight_list_analyzer_agent = init_flight_analyzer_agent()
        best_flight_result: RunResponse = flight_list_analyzer_agent.run(all_flights_results_str)
        best_flight_result = best_flight_result.content.model_dump()
        print("FFFFF: ", best_flight_result)
        #Adding a redirect URL
        for each_results in best_flight_result['flight_search_results']:
            redirect_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{each_results['destination_airport']}%20from%20{each_results['origin_airport']}%20on%20{each_results['Date']}%20one%20way%20economy%20class&curr=INR"
            each_results['redirect_url'] = redirect_url
            # redirect_url = # https://www.google.com/travel/flights?q=Flights%20to%20BDQ%20from%20BLR%20on%202025-05-27%20one%20way%20economy%20class&curr=
        print("*****"*10)
        print(best_flight_result)
            
    else:
        best_flight_result = input_json_response['ask_user_message']
    return best_flight_result


if __name__ == "__main__":

    best_flight_result = search_flights(user_query)
    # print("*****"*10)
    # print(best_flight_result)
