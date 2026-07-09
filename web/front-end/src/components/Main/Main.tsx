import styled from "styled-components";

export default function Main() {
  return <Wrapper></Wrapper>;
}

const Wrapper = styled.main`
  position: relative;
  overflow: hidden;

  background:
    radial-gradient(
      62.14% 67.71% at 90.48% 74.59%,
      rgba(249, 166, 0, 0.2) 0%,
      var(--superficie-secundaria, rgba(104, 34, 139, 0.2)) 100%
    ),
    radial-gradient(
      71.83% 36.1% at 19.56% 13.85%,
      rgba(98, 178, 227, 0.26) 0%,
      var(--superficie-secundaria, rgba(104, 34, 139, 0.26)) 100%
    ),
    var(--superficie-secundaria, #68228b);
`;
