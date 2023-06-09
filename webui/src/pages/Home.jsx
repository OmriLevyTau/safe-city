import { GoogleMap, useLoadScript } from "@react-google-maps/api";
import React, { useMemo, useState } from "react";
import "./Home.css";
import AddressesGoogleMapsAutoComplete from "./googleAddresses";

const fontFamily = "Geologica";
let routePolyline;

export default function AppHome() {
  const [selectedSource, setSelectedSource] = useState("");
  const [selectedDestination, setSelectedDestination] = useState("");
  const [map, setMap] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const { isLoaded } = useLoadScript({
    googleMapsApiKey: "AIzaSyCuKXnYCsXCRcJlWL4wuCD6CUkJoN0YNS8",
  });

  const center = useMemo(() => ({ lat: 32.0853, lng: 34.7818 }), []);
  const restriction = useMemo(
    () => ({
      latLngBounds: {
        north: 32.1409,
        south: 32.0406,
        east: 34.8695,
        west: 34.7172,
      },
      strictBounds: true,
    }),
    []
  );

  const updateMapWithRoute = (encodedPolyline) => {
    const decodedPath = new window.google.maps.geometry.encoding.decodePath(
      encodedPolyline
    );
    routePolyline = new window.google.maps.Polyline({
      path: decodedPath,
      geodesic: true,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 4,
    });

    
    const bounds = new window.google.maps.LatLngBounds();
    const pathCoordinates = decodedPath.map((coordinate) => [
      coordinate.lat(),
      coordinate.lng(),
    ]);
    pathCoordinates.forEach((coordinate) => {
      bounds.extend(
        new window.google.maps.LatLng(coordinate[0], coordinate[1])
      );
    });
    map.fitBounds(bounds);
    routePolyline?.setMap(map);
  };

  const handleSubmit = () => {
    setIsLoading(true);
    if (!selectedSource || !selectedDestination) {
      console.log("please fill address field");
    } else {
      fetch(
        `http://localhost:8000/home-search?src=${selectedSource}&dst=${selectedDestination}`
      )
        .then((result) => {
          return result.json();
        })
        .then((encodedPolyline) => {
          updateMapWithRoute(encodedPolyline.route);
          setIsLoading(false);
        })
        .then(() => addLine())
        .catch((err) => console.log("There was an error fetching the route"));
    }
  };

  const onLoad = (map) => {
    setMap(map);
  };
  function removeLine() {
    routePolyline?.setMap(null);
  }
  function addLine() {
    routePolyline?.setMap(map);
  }
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ width: "30%", marginTop: "15%", textAlign: "center" }}>
        <h1
          style={{
            fontSize: "5rem",
            color: "#F7F0E2",
            fontWeight: "bold",
            marginBottom: "20px",
          }}
        >
          Start Our Journey
        </h1>
        <AddressesGoogleMapsAutoComplete
          setSelectedAddresses={setSelectedSource}
          placeHolder="Where Are You At ?"
        />
        <AddressesGoogleMapsAutoComplete
          setSelectedAddresses={setSelectedDestination}
          placeHolder="Where Are You Want To Go ?"
        />
        <br />
        <button
          style={{
            borderRadius: "10px",
            width: "200px",
            height: "50px",
            fontFamily: fontFamily,
            fontSize: "2rem",
            backgroundColor: "#F7F0E2",
            transition: "background-color 0.3s ease",
          }}
          onClick={handleSubmit}
        >
          {!isLoading ? <>Let's Go !</> : <>Loading...</>}
        </button>
        <button
          style={{
            borderRadius: "10px",
            width: "200px",
            height: "50px",
            fontFamily: fontFamily,
            fontSize: "2rem",
            backgroundColor: "#F7F0E2",
            transition: "background-color 0.3s ease",
          }}
          onClick={removeLine}
        >
          Clear
        </button>
      </div>
      <div id="map" style={{ width: "70%" }}>
        {!isLoaded ? (
          <h1>Loading...</h1>
        ) : (
          <GoogleMap
            mapContainerClassName="map-container"
            center={center}
            zoom={0}
            onLoad={onLoad}
            options={{ restriction: restriction }}
          />
        )}
      </div>
    </div>
  );
}
