import styled from "styled-components";

export default function MissionSelector() {
  return (
    <Wrapper>
      <label for="pet-select">Missões:</label>
      <Select>
        <option value="">Selecione uma missão:</option>
        <option value="#11">#11 Foguete principal</option>
        <option value="#51">#51 Foguete Secundário</option>
        <option value="#213">#213 Satélite</option>
      </Select>
    </Wrapper>
  );
}

const Wrapper = styled.div`
  display: flex;
  flex-direction: column;
  width: fit-content;
  margin-block: 30px 0;
  margin-inline: auto;

  font-family: Jersey10;
  font-size: 40px;
  color: white;
`;

const Select = styled.select`
  font-family: Jersey10;
  font-size: 40px;
  color: #68228b;
`;
