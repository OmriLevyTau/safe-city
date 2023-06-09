from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import requests
import os
import numpy as np

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/home-search")
async def welcome(src:str, dst:str):
    maps_api_key = "AIzaSyCuKXnYCsXCRcJlWL4wuCD6CUkJoN0YNS8"
    safe_city = SafeCity(maps_api_key)
    route = safe_city.get_routes(src.replace(" ", "+"), dst.replace(" ", "+"))
    return {"route": route[0]}



class SafeCity:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_street_score(self, street_name):
        return random.randint(0, 1000)

    def get_route_score(self, route):
        streets = self.get_streets_from_route(route)
        score = 0
        for street in streets:
            score += self.get_street_score(street)
        return score

    def get_streets_from_route(self, route):
        streets = set()
        for leg in route['legs']:
            for step in leg['steps']:
                start_lat, start_lng = step['start_location']['lat'], step['start_location']['lng']
                end_lat, end_lng = step['end_location']['lat'], step['end_location']['lng']
                start_street = self.get_street_from_latlng(start_lat, start_lng)
                end_street = self.get_street_from_latlng(end_lat, end_lng)
                SafeCity.append_if_not_none([start_street, end_street], streets)
        return streets

    @staticmethod
    def append_if_not_none(elems, st):
        for elem in elems:
            if elem is not None:
                st.add(elem)

    def get_request_wrapper(self, url, params):
        params['key'] = self.api_key
        res = requests.get(url, params)
        res.raise_for_status()
        json_results = res.json()
        if json_results['status'] == 'ZERO_RESULTS':
            return {}
        if json_results['status'] != "OK":
            raise Exception("Error performing http request: ", json_results['error_message'])
        return json_results

    def get_street_from_latlng(self, lat, lng):
        url = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = {
            "latlng": f"{lat},{lng}",
            "result_type": "street_address"
        }
        json_results = self.get_request_wrapper(url, params)
        if not json_results:
            return None
        for result in json_results['results']:
            for adc in result['address_components']:
                if "route" in adc["types"]:
                    return adc['long_name']
        return None

    def get_routes(self, origin, destination, waypoints=None):
        url = "https://maps.googleapis.com/maps/api/directions/json?"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "walking",
            "alternatives": "true",
        }
        if waypoints is not None:
            params['waypoints'] = f"{'|'.join(waypoints)}"

        json_results = self.get_request_wrapper(url, params)
        routes = json_results['routes']
        scores = np.array([self.get_route_score(route) for route in routes])
        srtd_args = - np.argsort(- scores)
        encoded_routes = [routes[idx]['overview_polyline']['points'] for idx in srtd_args]
        return encoded_routes

    def calculate_bounding_box(self, lat1, lon1, lat2, lon2):
        min_lat = min(lat1, lat2)
        max_lat = max(lat1, lat2)
        min_lng = min(lon1, lon2)
        max_lng = max(lon1, lon2)
        return min_lat, max_lat, min_lng, max_lng

    def sample_points_in_box(self, source, destination, num_points):
        min_lat, max_lat, min_lng, max_lng = self.calculate_bounding_box(*source, *destination)
        lats = np.random.uniform(low=min_lat, high=max_lat, size=num_points)
        lngs = np.random.uniform(low=min_lng, high=max_lng, size=num_points)
        return lats, lngs

    def get_closest_street(self, lat, lng):
        return

    def get_street_with_max_score(self, streets):
        max_score = 0
        best_street = None
        for street in streets:
            curr_score = self.get_street_score(street)
            if curr_score >= max_score:
                best_street = street
        return best_street

    def sample_from_street(self, street_name):
        return
