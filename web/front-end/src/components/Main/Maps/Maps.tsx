import Card from "@/shared/Cards/Card";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { FullscreenControl } from "react-leaflet-fullscreen";
import "react-leaflet-fullscreen/styles.css";
import styled from "styled-components";

import type { webSocketData } from "@components/Main/Main";

type Coords = Pick<webSocketData, "latitude" | "longitude">;

interface MapsProps {
  missionCoords?: Coords;
}

export default function Maps({ missionCoords }: MapsProps) {
  return (
    <Wrapper title="Coordenadas">
      {missionCoords && (
        <MapContainer
          center={[missionCoords.latitude, missionCoords.longitude]}
          zoom={13}
          scrollWheelZoom={true}
          zoomControl={false}
        >
          <TileLayer
            attribution={
              "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, " +
              "USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, " +
              "and the GIS User Community"
            }
            url={
              "https://server.arcgisonline.com/ArcGIS/rest/services/" +
              "World_Imagery/MapServer/tile/{z}/{y}/{x}"
            }
          />
          <Marker position={[missionCoords.latitude, missionCoords.longitude]}>
            <Popup>Posição da missão</Popup>
          </Marker>
          <FullscreenControl />
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
