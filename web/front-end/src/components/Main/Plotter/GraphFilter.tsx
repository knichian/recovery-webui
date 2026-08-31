import styled from "styled-components";

import type { GraphsFilter } from "./Plotter";
import bulletIconSrc from "./rocket.svg";

interface GraphsFilterMenuProps {
  filter: GraphsFilter;
  setFilter: React.Dispatch<React.SetStateAction<GraphsFilter>>;
}

export default function GraphsFilterMenu({
  filter,
  setFilter,
}: GraphsFilterMenuProps) {
  function handleChange(key: string) {
    setFilter((prev) => {
      return {
        ...prev,
        [key]: !prev[key],
      };
    });
  }

  return (
    <Wrapper>
      <List $bulletIconSrc={bulletIconSrc}>
        {Object.entries(filter).map(([key, value]) => {
          if (key === "time") return;
          return (
            <li key={key}>
              <span>{key}</span>
              <input
                type="checkbox"
                checked={value}
                onChange={() => handleChange(key)}
              />
            </li>
          );
        })}
      </List>
    </Wrapper>
  );
}

const Wrapper = styled.div`
  width: fit-content;
  position: absolute;
  top: 80px;
  left: 0;
`;

const List = styled.ul<{ $bulletIconSrc: string }>`
  list-style: url("${({ $bulletIconSrc }) => $bulletIconSrc}");
`;
