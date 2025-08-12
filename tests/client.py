import requests

URL = "http://0.0.0.0:3001/api/v1/searchFlights"

req_body = {
  "user_query": "Look for Bangalore to Ahmedabad best flights for 1 person in June 2025"
}

response = requests.post(f"{URL}/12345", json=req_body)
print(response.text)