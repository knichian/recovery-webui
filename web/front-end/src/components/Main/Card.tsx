import type { PropsWithChildren } from "react";
import styled from "styled-components";

export function Card({
  title,
  children,
  className,
}: PropsWithChildren<CardProps>) {
  return (
    <Wrapper className={className}>
      <CardTitle>{title}</CardTitle>
      {children}
    </Wrapper>
  );
}

interface CardProps {
  title: string;
  className?: string;
}

const Wrapper = styled.div`
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
