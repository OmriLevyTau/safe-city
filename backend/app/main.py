from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
import numpy as np
import jq
import json
import geopandas as gpd
from shapely.geometry import LineString
from shapely.geometry import Point


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

streets_db = pd.read_csv(".//resources//final.csv")
MEAN_SCORE = streets_db["normalized_lights_per_meter"].mean()


def load_streets_metadata():
    with open("./resources/streets.json", 'r') as f:
        data = json.load(f)
    data = data["features"]

    geometries = [LineString(feature['geometry']['paths'][0]) for feature in data]
    attributes = [feature['attributes'] for feature in data]
    df = gpd.GeoDataFrame(attributes, geometry=geometries)
    return df


streets_metadata = load_streets_metadata()


@app.get("/home-search")
async def welcome(src: str, dst: str):
    maps_api_key = "AIzaSyCuKXnYCsXCRcJlWL4wuCD6CUkJoN0YNS8"
    safe_city = SafeCity(maps_api_key)
    route = safe_city.get_routes(src.replace(" ", "+"), dst.replace(" ", "+"), num_waypoints=10)
    return {"route": route[0]}


class SafeCity:
    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def get_street_score(street_name):
        for index, row in streets_db.iterrows():
            row_name = row["shem_angli"]
            if row_name in street_name.lower():
                return row["normalized_lights_per_meter"]
        return MEAN_SCORE

    def get_route_score(self, route):
        streets = self.get_streets_from_route(route)
        score = 0
        for street in streets:
            score += self.get_street_score(street)
        return score / len(streets)

    def get_streets_from_route(self, route):
        lat_langs = jq.compile('.legs[].steps[] | {latlng: [.start_location.lat, .start_location.lng] | '
                               '@csv, latlng: [.end_location.lat, .end_location.lng] | @csv}.latlng').input(route).all()
        vfunc = np.vectorize(self.get_street_from_latlng)
        return set(vfunc(lat_langs))

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

    def get_street_from_latlng(self, latlng):
        url = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = {
            "latlng": latlng,
            "result_type": "street_address"
        }
        json_results = self.get_request_wrapper(url, params)
        if not json_results:
            return None
        return jq.compile('.results[0].address_components[] | '
                          'select(.types | index("route")).short_name').input(json_results).first()

    def get_routes(self, origin, destination, num_waypoints=None):
        waypoints = self.sample_waypoints(origin, destination, num_waypoints)
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

    def calculate_bounding_box(self, origin, destination):
        url = "https://maps.googleapis.com/maps/api/directions/json?"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "walking",
            "alternatives": "true",
        }
        json_results = self.get_request_wrapper(url, params)
        bounds = jq.compile('.routes[0].bounds | .northeast, .southwest').input(json_results).all()
        return bounds

    def sample_points_in_box(self, source, destination, num_points):
        bounds = self.calculate_bounding_box(source, destination)
        lats = np.random.uniform(low=bounds[0]['lat'], high=bounds[1]['lat'], size=num_points)
        lngs = np.random.uniform(low=bounds[0]['lng'], high=bounds[1]['lng'], size=num_points)
        return lats, lngs

    @staticmethod
    def get_closest_street(lat, lng):
        xy = Point(lat, lng)
        closest_street = streets_metadata.loc[streets_metadata["geometry"].distance(xy).idxmin()]
        return closest_street

    def get_street_with_max_score(self, streets):
        max_score = 0
        best_street = None
        for street in streets:
            street_name = street["shem_angli"].lower()
            curr_score = self.get_street_score(street_name)
            if curr_score >= max_score:
                best_street = street
        return best_street

    @staticmethod
    def sample_from_street(street):
        zipped_points = list(zip(street['geometry'].xy[0],street['geometry'].xy[1])) 
        start, end = zipped_points[0], zipped_points[-1]
        lats = np.random.uniform(low=start[0], high=end[0], size=2)
        lngs = np.random.uniform(low=start[1], high=end[1], size=2)
        return lats, lngs

    def sample_waypoints(self, origin, destination, num_waypoints):
        streets = []
        lats, lngs = self.sample_points_in_box(origin, destination, num_waypoints)
        for lat, lng in zip(lats, lngs):
            streets.append(self.get_closest_street(lng, lat))
        best_street = self.get_street_with_max_score(streets)
        waypoints_lats, waypoints_langs = self.sample_from_street(best_street)
        waypoints = [f"{waypoints_langs[i]},{waypoints_lats[i]}" for i in range(len(waypoints_langs))]
        return waypoints
