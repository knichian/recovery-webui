import styled from "styled-components";

export default function RenderSocket() {
  return (
    <Wrapper>
      <Data>{"Dados"}</Data>
      <Data>{"Dados"}</Data>
      <Data>{"Dados"}</Data>
      <Data>{"Dados"}</Data>
      <Data>{"Dados"}</Data>
      <Data>{"Dados"}</Data>
      <Data>{"Dados"}</Data>
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
`;

const Data = styled.p`
  color: #fff;
  font-family: Jersey10;
  font-size: 46px;
  margin: 0;
`;
