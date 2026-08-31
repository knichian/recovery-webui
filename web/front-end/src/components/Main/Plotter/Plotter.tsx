import Card from "@/shared/Cards/Card";
import { useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  Tooltip,
  XAxis,
  YAxis,
  createHorizontalChart,
} from "recharts";
import styled from "styled-components";

import type { WebSocketData } from "@components/Main/Main";

import FullscreenButton from "./FullscreenButton";
import IconSrc from "./icon-fullscreen.svg";

interface PlotterProps {
  data: WebSocketData[];
}

export default function Plotter({ data }: PlotterProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const Typed = createHorizontalChart<WebSocketData, string, number>()({
    Line,
    XAxis,
    YAxis,
  });

  function handleButtonClick() {
    setIsFullscreen(!isFullscreen);
  }

  const cardContent = (
    <>
      <FullscreenButton
        $src={IconSrc}
        $isFullscreen={isFullscreen}
        onClick={handleButtonClick}
      />
      <Typed.LineChart
        style={{ width: "90%", height: "100%", alignSelf: "flex-end" }}
        margin={{ right: 40, bottom: 10, top: 10 }}
        responsive
        data={isFullscreen ? data.slice(-100) : data.slice(-20)}
      >
        <CartesianGrid />
        <Typed.XAxis dataKey="time" />
        <Typed.YAxis dataKey="altura" />
        <Typed.Line isAnimationActive={false} dataKey="altura" />
        <Legend />
        <Tooltip isAnimationActive={false} />
      </Typed.LineChart>
    </>
  );

  return (
    <Wrapper isFullscreen={isFullscreen} title="Plotter">
      {cardContent}
    </Wrapper>
  );
}

const Wrapper = styled(Card)`
  grid-row: 2 / span 1;
  grid-column: 1 / span 4;

  @media (min-width: 768px) {
    grid-row: 2 / span 1;
    grid-column: 1 / span 5;
  }

  @media (min-width: 1280px) {
    grid-row: 2 / span 1;
    grid-column: 1 / span 8;
  }
`;
