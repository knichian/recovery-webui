import styled from "styled-components";
import Logo from "@components/Header/Logo";
import logoSrc from "@images/logo-serra-small.svg";

function Header() {
  return (
    <Wrapper>
      <Logo logoSrc={logoSrc} alt="Logo sem texto da Equipe Serra Rocketry" />
      <HeaderText>CONTROLE DE MISSÃO</HeaderText>
    </Wrapper>
  );
}

const Wrapper = styled.header`
  display: flex;
  padding: 15px 20px;
  justify-content: space-between;
  background-color: var(--superficie-invertida, #fff);
`;

const HeaderText = styled.div`
  color: var(--texto-marca, #68228b);
  font-family: Iceland;
  font-size: 30px;
`;

export default Header;
