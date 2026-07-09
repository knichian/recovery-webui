import styled from "styled-components";

import { Card } from "./Card";

export default function Maps() {
  return <Wrapper className={"mapsCard"} title="Coordenadas"></Wrapper>;
}

const Wrapper = styled(Card)`
  grid-row: 1 / span 1;
  grid-column: 1 / span 4;
`;
