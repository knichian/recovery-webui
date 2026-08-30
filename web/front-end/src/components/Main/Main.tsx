import Cards from "@/shared/Cards/Cards";
import socket from "@/websocket/websocket";
import { useEffect, useState } from "react";
import styled from "styled-components";

import Maps from "./Maps/Maps";
import Plotter from "./Plotter/Plotter";
import RenderSocket from "./RenderSocket";

export interface webSocketData {
  [key: string]: number | string;
  latitude: number;
  longitude: number;
  altura: number;
  satelites: number;
  temperatura: number;
  pressao: number;
  rssi: number;
  time: string;
}

export default function Main() {
  const [data, setData] = useState<webSocketData>();

  useEffect(() => {
    function handleEvent(payload: webSocketData) {
      setData(payload);
    }

    socket.on("updateSat", handleEvent);

    return () => {
      socket.off("updateSat", handleEvent);
    };
  }, []);

  return (
    <Wrapper>
      <Cards>
        <Maps missionCoords={data} />
        <Plotter />
        <RenderSocket data={data} />
      </Cards>
    </Wrapper>
  );
}

const Wrapper = styled.main`
  flex: 1;
  background:
    radial-gradient(
      62.14% 67.71% at 90.48% 74.59%,
      rgba(249, 166, 0, 0.2) 0%,
      var(--superficie-secundaria, rgba(104, 34, 139, 0.2)) 100%
    ),
    radial-gradient(
      71.83% 36.1% at 19.56% 13.85%,
      rgba(98, 178, 227, 0.26) 0%,
      var(--superficie-secundaria, rgba(104, 34, 139, 0.26)) 100%
    ),
    var(--superficie-secundaria, #68228b);
`;
