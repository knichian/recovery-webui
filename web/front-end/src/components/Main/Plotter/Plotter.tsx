import Card from "@/shared/Cards/Card";
import styled from "styled-components";

export default function Plotter() {
  return <Wrapper title="Plotter"></Wrapper>;
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
