import Cards from "@/shared/Cards/Cards";
import socket from "@/websocket/websocket";
import { useEffect, useState } from "react";
import styled from "styled-components";

import Maps from "./Maps/Maps";
import Plotter from "./Plotter/Plotter";
import RenderSocket from "./RenderSocket";

export interface WebSocketData {
  [key: string]: string | number | Date;
  altura: number;
  latitude: number;
  longitude: number;
  pressao: number;
  rssi: number;
  satelites: number;
  temperatura: number;
  time: string;
}

export default function Main() {
  const [data, setData] = useState<WebSocketData[]>([]);

  useEffect(() => {
    function handleEvent(payload: WebSocketData) {
      setData((prev) => [
        ...prev,
        {
          altura: Number(payload.altura),
          latitude: Number(payload.latitude),
          longitude: Number(payload.longitude),
          pressao: Number(payload.pressao),
          rssi: Number(payload.rssi),
          satelites: Number(payload.satelites),
          temperatura: Number(payload.altura),
          time: new Date(payload.time).toTimeString().split(" ")[0],
        },
      ]);
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
        <Plotter data={data} />
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
