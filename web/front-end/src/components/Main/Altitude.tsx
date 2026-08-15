import Card from "@/shared/Cards/Card";
import styled from "styled-components";

export default function Altitude() {
  return <Wrapper className="altitudeCard" title="Altitude"></Wrapper>;
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
