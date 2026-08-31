import Card from "@/shared/Cards/Card";
import { useEffect, useState } from "react";
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
import GraphsFilterMenu from "./GraphFilter";
import IconSrc from "./icon-fullscreen.svg";

interface PlotterProps {
  data: WebSocketData[];
}

export interface GraphsFilter {
  [key: string]: boolean;
}

export default function Plotter({ data }: PlotterProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [graphsFilter, setGraphsFilter] = useState<GraphsFilter>({});

  let dataKeys: string[] = [];
  if (data.length > 0) {
    dataKeys = Object.keys(data[0]);
  }

  useEffect(() => {
    if (Object.keys(graphsFilter).length > 0) {
      return;
    }
    setGraphsFilter(Object.fromEntries(dataKeys.map((key) => [key, true])));
  }, [data]);

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
      <GraphsFilterMenu filter={graphsFilter} setFilter={setGraphsFilter} />
      <Typed.LineChart
        style={{
          width: isFullscreen ? "90%" : "70%",
          height: "100%",
          alignSelf: "flex-end",
        }}
        margin={{ right: 40, bottom: 10, top: 10 }}
        responsive
        data={isFullscreen ? data.slice(-100) : data.slice(-20)}
      >
        <CartesianGrid />
        <Typed.XAxis dataKey="time" />
        <Typed.YAxis />
        <Typed.YAxis />
        {dataKeys
          .filter((key) => graphsFilter[key])
          .map((key) => {
            if (key === "time") return;
            return (
              <Typed.Line key={key} isAnimationActive={false} dataKey={key} />
            );
          })}
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
