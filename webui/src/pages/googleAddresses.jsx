import React from "react";
import PlacesAutocomplete, {
  geocodeByAddress,
} from "react-places-autocomplete";
import "./Home.css";
import { useState } from "react";
import { Input } from "antd";

export default function AddressesGoogleMapsAutoComplete({
  setSelectedAddresses,
  placeHolder,
}) {
  const [address, setAddress] = useState("");
  const google = window.google;

  const searchOptions = {
    location: new google.maps.LatLng(31.4117, 35.0818155),
    componentRestrictions: {
      country: "il",
    },
    radius: 2000,
    types: ["address"],
    language: "en",
  };

  const handleSelect = async (value) => {
    try {
      await geocodeByAddress(value, { language: "en" });
      setSelectedAddresses(value);
      setAddress(value);
    } catch {
      console.log("falid to fetch addr ! ");
      alert("Invalid Address");
      setAddress("");
    }
  };

  const handlerChange = (newAddress) => {
    setAddress(newAddress);
    setSelectedAddresses(newAddress);
  };

  return (
    <>
      <PlacesAutocomplete
        value={address}
        onChange={(newValue) => handlerChange(newValue)}
        onSelect={handleSelect}
        searchOptions={searchOptions}
      >
        {({ getInputProps, suggestions, getSuggestionItemProps, loading }) => (
          <div>
            <Input
              required={true}
              name={"address"}
              label={"Full Address"}
              {...getInputProps({
                placeholder: placeHolder,
              })}
              style={{
                width: "80%",
                height: "50px",
                fontSize: "24px",
                backgroundColor: "#D7C0AE",
                marginTop: "20px",
                language: "en",
              }}
            />
            {loading ? (
              <div
                {...getSuggestionItemProps(suggestions)}
                style={{ color: "#D7C0AE", backgroundColor: "#2C2C2C" }}
              >
                Loading ...
              </div>
            ) : null}
            {suggestions?.map((suggestion) => {
              const style = {
                color: "#D7C0AE",
                backgroundColor: "#2C2C2C",
                language: "en",
                width: "80%",
              };
              return (
                <div {...getSuggestionItemProps(suggestion, { style })}>
                  {suggestion?.description}
                </div>
              );
            })}
          </div>
        )}
      </PlacesAutocomplete>
    </>
  );
}
