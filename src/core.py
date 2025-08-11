import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from typing import List, Dict, Any, Optional

from fast_flights import create_filter, get_flights_from_filter, FlightData, Passengers
from src.json_schema import FlightJSON, Result
from src.logger import get_default_logger
import uuid
from datetime import datetime, timedelta
import calendar

# Setup logger
logger = get_default_logger(__name__)

def get_dates_for_month(month_year: str):
    date_obj = datetime.strptime(month_year, "%B %Y")
    year = date_obj.year
    month = date_obj.month

    num_days = calendar.monthrange(year, month)[1]

    # Generate date list
    return [f"{year}-{month:02d}-{day:02d}" for day in range(1, num_days + 1)]

# Function to process a single date (to be run in parallel)
def process_date(date_params, date):
    each_date = date
    from_airport = date_params['from_airport']
    to_airport = date_params['to_airport']
    adults = date_params['adults']
    children = date_params['children']
    infants_in_seat = date_params['infants_in_seat']
    infants_on_lap = date_params['infants_on_lap']
    trip_type = ''.join(date_params['trip_type']),
    seat = date_params['seat']
    max_stops = date_params['max_stops']
    logger.info(f"Processing date: {each_date}")

    filter = None
    logger.debug(f"Trip type: {trip_type}, Date: {each_date}")
    if trip_type[0] == 'one-way':  
        filter = create_filter(
            flight_data=[
                FlightData(
                    date=str(each_date),
                    from_airport=from_airport,
                    to_airport=to_airport,
                )
            ],
            trip="one-way",
            passengers=Passengers(adults=adults, children=children, infants_in_seat=infants_in_seat, 
                                infants_on_lap=infants_on_lap),
            seat=seat,
            max_stops=max_stops,
        )
    
    result_data = get_flights_from_filter(filter, mode="common")
    
    flights = [
        FlightJSON(
            flight.is_best, flight.name, flight.departure, flight.arrival, 
            flight.arrival_time_ahead, flight.duration, flight.stops, 
            flight.delay, flight.price
        )
        for flight in result_data.flights
    ]
    
    flight_json = Result(result_data.current_price, flights).to_dict()
    
    # Return both the date and the flight info for later processing
    return {
        "date": each_date,
        "flight_info": flight_json,
        "price": result_data.current_price
    }

# Main function using ThreadPoolExecutor for parallel processing
def search_flights_parallel(user_filters, max_workers=10):
    logger.info(f"Starting parallel flight search with {max_workers} workers")
    logger.info(f"Search parameters: {user_filters}")
    
    # Get all dates for the month
    date_list = user_filters['date_list']
    logger.info(f"Processing {len(date_list)} dates: {date_list}")
    
    all_date_flight_info = []
    all_added_flight_ids = []
    specific_flight_provider = []
    min_price = float('inf')
    max_price = 0
    
    # Create a lock for thread-safe operations
    price_lock = threading.Lock()
    results_lock = threading.Lock()
    
    # Use ThreadPoolExecutor to manage threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        logger.info(f"Submitting {len(date_list)} tasks to thread pool")
        # Submit all tasks and get future objects
        future_to_date = {executor.submit(process_date, user_filters, date): date for date in date_list}
        
        # Process results as they complete
        for future in future_to_date:
            try:
                result = future.result()
                date = result["date"]
                flight_info = result["flight_info"]
                price_status = result["price"]
                logger.debug(f"Processing result for date: {date}")
                
                # Thread-safe operations for shared resources
                with results_lock:
                    for each_flight in flight_info['flights']:
                        each_flight['date'] = date
                        each_flight['id'] = str(uuid.uuid4())
                        if len(user_filters['specific_flight_provider']) < 1:
                            if each_flight['name'].lower() not in specific_flight_provider:
                                specific_flight_provider.append(each_flight['name'].lower())
                        else: 
                            specific_flight_provider = user_filters['specific_flight_provider']

                        logger.debug(f"Flight provider: {specific_flight_provider}")
                        if (each_flight['is_best'] == True  
                            and each_flight['name'].lower() in specific_flight_provider  #
                            and each_flight['stops'] <= user_filters['max_stops'] 
                            and each_flight['id'] not in all_added_flight_ids):
                                all_date_flight_info.append(each_flight)
                                all_added_flight_ids.append(each_flight['id'])
                                logger.info(f"Added best flight: {each_flight['id']} for date {date}")
                        # if each_flight['name'].lower() in user_filters['specific_flight_provider'] and each_flight['id'] not in all_added_flight_ids:
                        #     all_date_flight_info.append(each_flight)
                        #     all_added_flight_ids.append(each_flight['id'])
                        #     logger.info(f"Added specific flight: {each_flight['id']}")
                        # Add condition only if we're looking out for non-best with other filters

                
            except Exception as exc:
                logger.error(f"Date {future_to_date[future]} generated an exception ")
    
    # Sort results by date for consistency
    all_date_flight_info.sort(key=lambda x: x["date"])
    logger.info(f"Total flights found: {len(all_added_flight_ids)}")
    logger.info(f"Best flights found: {len(all_date_flight_info)}")
    
    return {
        "flight_info": all_date_flight_info,
        "user_inputs": user_filters
    }

# Example usage
if __name__ == "__main__":
    logger.info("Starting core.py main execution")
    start_time = time.time()
    
    month_to_search = "May 2025"
    date_list = get_dates_for_month(month_to_search)
    logger.info(f"Found {len(date_list)} dates to process: {date_list}")
    
    user_filters = {
        "from_airport": "BDQ",
        "to_airport": "BLR",
        "adults": 1,
        "children": 0,
        "infants_in_seat": 0,
        "infants_on_lap": 0,
        "trip_type": "one-way",
        "seat": "economy",
        "date_list": date_list,
        "specific_flight_provider": [],
        "flight_time_type": [],
        "max_stops": 1,
        "price_type": 'minimum'
    }
    logger.info(f"User filters configured: {user_filters}")
    
    try:
        results = search_flights_parallel(user_filters)
        logger.info("Flight search completed successfully")
        
        logger.info("Results summary:")
        logger.info(f"Total flights found: {len(results['flight_info'])}")
        
        # Log the results
        logger.info(f"Results: {results}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Save results to file
        with open("flights.json", 'w') as fp:
            json.dump(results, fp)
        logger.info(f"Results saved to flights.json")
        
        logger.info(f"Total execution time: {execution_time:.2f} seconds")
        logger.info("Core.py main execution completed successfully")
        
    except Exception as e:
        logger.error(f"Error during main execution: {e}")
        raise