import styled from "styled-components";
import Logo from "@components/Header/Logo";

function Header() {
  return (
    <Wrapper>
      <Logo />
      <HeaderText>CONTROLE DE MISSÃO</HeaderText>
    </Wrapper>
  );
}

const Wrapper = styled.header`
  display: flex;
  gap: 5px;
  height: 60px;
  padding-block: 10px;
  padding-inline: 20px;
  justify-content: space-between;
  align-items: center;
  background-color: var(--superficie-invertida, #fff);

  @media (min-width: 768px) {
    height: 80px;
    padding-block: 15px;
  }
`;

const HeaderText = styled.span`
  color: var(--texto-marca, #68228b);
  font-family: Iceland;
  font-size: 30px;
  text-align: right;

  @media (min-width: 768px) {
    font-size: 40px;
  }
`;

export default Header;
