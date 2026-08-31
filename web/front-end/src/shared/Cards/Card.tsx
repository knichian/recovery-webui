import type { PropsWithChildren } from "react";
import styled from "styled-components";

function Card({
  title,
  children,
  className,
  isFullscreen = false,
}: PropsWithChildren<CardProps>) {
  return (
    <Wrapper className={className} $isFullscreen={isFullscreen}>
      <CardTitle>{title}</CardTitle>
      {children}
    </Wrapper>
  );
}

interface CardProps {
  title: string;
  isFullscreen?: boolean;
  className?: string;
}

function handleIsFullscreen(isFullscreen: boolean) {
  if (isFullscreen) {
    return `
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      max-height: unset;
      z-index: 1000;
      width: 100dvw;
      height: 100dvh;
      border-radius: 0;
    `;
  }
}

const Wrapper = styled.div<{ $isFullscreen: boolean }>`
  width: 100%;
  max-height: 300px;
  justify-self: stretch;
  display: flex;
  flex-direction: column;
  align-items: center;
  aspect-ratio: 1/1;
  border-radius: 20px;
  background: var(--superficie-invertida, #fff);
  position: relative;
  overflow: hidden;

  /* Card Shadow */
  box-shadow: 6px 4px 16px 2px rgba(0, 0, 0, 0.25);

  /* Fullscreen styles overwrite */
  ${({ $isFullscreen }) => handleIsFullscreen($isFullscreen)}
`;

const CardTitle = styled.p`
  margin: 0;
  padding-block: 5px;
  background-color: white;
  width: 100%;
  color: var(--texto-texto-marca, #68228b);
  font-family: Jersey10;
  font-size: 32px;
  text-align: center;
`;

export default Card;
