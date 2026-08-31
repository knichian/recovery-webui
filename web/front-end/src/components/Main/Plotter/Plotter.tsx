import Card from "@/shared/Cards/Card";
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

interface PlotterProps {
  data: WebSocketData[];
}

export default function Plotter({ data }: PlotterProps) {
  const Typed = createHorizontalChart<WebSocketData, string, number>()({
    Line,
    XAxis,
    YAxis,
  });

  const cardContent = (
    <>
      <Typed.LineChart
        style={{ width: "100%", height: "100%", alignSelf: "flex-end" }}
        margin={{ right: 40, bottom: 10, top: 10 }}
        responsive
        data={data.slice(-20)}
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

  return <Wrapper title="Plotter">{cardContent}</Wrapper>;
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
