import useDeviceCompass from "@/customHooks/useDeviceCompass";
import Card from "@/shared/Cards/Card";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { FullscreenControl } from "react-leaflet-fullscreen";
import "react-leaflet-fullscreen/styles.css";
import styled from "styled-components";

import type { webSocketData } from "@components/Main/Main";
import GyroscopeControl from "@components/Main/Maps/GyroscopeControls";
import customIconSrc from "@components/Main/Maps/marker.svg";

type Coords = Pick<webSocketData, "latitude" | "longitude">;

interface MapsProps {
  missionCoords?: Coords;
}

export default function Maps({ missionCoords }: MapsProps) {
  const [userCoords, setUserCoords] = useState<Coords>();

  const { compassRequestStatus, setCompassRequestStatus } = useDeviceCompass();

  useEffect(() => {
    const handlerID = navigator.geolocation.watchPosition(
      ({ coords: userCoords }) => {
        setUserCoords({
          latitude: userCoords.latitude,
          longitude: userCoords.longitude,
        });
      },
    );

    return () => {
      navigator.geolocation.clearWatch(handlerID);
    };
  }, []);

  const customIcon = new L.Icon({
    iconUrl: customIconSrc,
    iconSize: new L.Point(40, 40),
    iconAnchor: new L.Point(20, 40),
  });
  const maxBoundOffset = 0.2;

  return (
    <Wrapper title="Coordenadas">
      {missionCoords && (
        <MapContainer
          center={[missionCoords.latitude, missionCoords.longitude]}
          scrollWheelZoom={true}
          zoomControl={false}
          zoom={13}
          minZoom={12}
          maxZoom={16}
          maxBounds={[
            [
              Number(missionCoords.latitude) - maxBoundOffset,
              Number(missionCoords.longitude) - maxBoundOffset,
            ],
            [
              Number(missionCoords.latitude) + maxBoundOffset,
              Number(missionCoords.longitude) + maxBoundOffset,
            ],
          ]}
        >
          <TileLayer
            attribution={
              "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, " +
              "USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, " +
              "and the GIS User Community"
            }
            url="/ArcGIS/{z}/{x}/{y}.png"
          />
          <Marker
            position={[missionCoords.latitude, missionCoords.longitude]}
            icon={customIcon}
          >
            <Popup>Posição da missão</Popup>
          </Marker>
          {userCoords && (
            <Marker
              position={[userCoords.latitude, userCoords.longitude]}
              icon={customIcon}
            >
              <Popup>Você!</Popup>
            </Marker>
          )}
          <FullscreenControl />
          <GyroscopeControl
            compassRequestStatus={compassRequestStatus}
            setCompassRequestStatus={setCompassRequestStatus}
          />
        </MapContainer>
      )}
    </Wrapper>
  );
}

const Wrapper = styled(Card)`
  grid-row: 1 / span 1;
  grid-column: 1 / span 4;
  overflow: hidden;

  @media (min-width: 768px) {
    grid-row: 1 / span 1;
    grid-column: 1 / span 5;
  }

  @media (min-width: 1280px) {
    grid-row: 1 / span 1;
    grid-column: 1 / span 8;
  }
`;
