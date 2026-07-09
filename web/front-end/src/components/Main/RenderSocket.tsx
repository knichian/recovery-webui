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
`;

const Data = styled.p`
  color: #fff;
  font-family: Jersey10;
  font-size: 46px;
  margin: 0;
`;
