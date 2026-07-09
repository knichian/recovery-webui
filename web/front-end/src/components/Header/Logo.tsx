import styled from "styled-components";
import logoSrc from "@images/logo-serra.svg";
import logoTextSrc from "@images/logo-serra-text.svg";

function Logo() {
  return (
    <Wrapper>
      <Img
        src={logoSrc}
        alt="Parte não-verbal da Logo da Equipe Serra Rocketry"
      />
      <Img
        src={logoTextSrc}
        alt="Parte verbal da Logo da Equipe Serra Rocketry"
        $hideOnMobile
      />
    </Wrapper>
  );
}

const Wrapper = styled.div`
  display: flex;
  gap: 10px;

  @media (min-width: 768px) {
    align-self: stretch;
  }
`;

const Img = styled.img<{ $hideOnMobile?: boolean }>`
  height: 100%;
  display: ${({ $hideOnMobile }) => ($hideOnMobile ? "None" : "")};

  @media (min-width: 768px) {
    display: block;
  }
`;

export default Logo;
