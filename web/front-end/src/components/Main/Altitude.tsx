import styled from "styled-components";

import { Card } from "./Card";

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
`;
