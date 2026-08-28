import styled from "styled-components";

import type { webSocketData } from "@components/Main/Main";

interface RenderSocketProps {
  data?: webSocketData;
}

export default function RenderSocket({ data }: RenderSocketProps) {
  return (
    <Wrapper>
      {data &&
        Object.keys(data).map((key) => (
          <Data>
            {key}: {data[key]}
          </Data>
        ))}
    </Wrapper>
  );
}

const Wrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  align-self: stretch;
  grid-row: span 1;
  grid-column: span 4;
  justify-self: stretch;

  @media (min-width: 768px) {
    grid-row: 1 / span 2;
    grid-column: 6 / span 3;
  }

  @media (min-width: 1280px) {
    grid-row: 1 / span 2;
    grid-column: 9 / span 4;
  }
`;

const Data = styled.p`
  color: #fff;
  font-family: Jersey10;
  font-size: 36px;
  margin: 0;
`;
