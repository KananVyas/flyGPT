import json
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