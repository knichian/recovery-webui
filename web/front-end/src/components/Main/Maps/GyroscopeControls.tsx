import type { CompassRequestStatus } from "@hooks/useDeviceCompass";
import { useEffect } from "react";
import Control from "react-leaflet-custom-control";
import styled from "styled-components";

import gyroscopeIconSrc from "@components/Main/Maps/gyroscope.svg";

interface GyroscopeControlProps {
  compassRequestStatus: CompassRequestStatus;
  setCompassRequestStatus: React.Dispatch<
    React.SetStateAction<CompassRequestStatus>
  >;
}

function GyroscopeControl({
  compassRequestStatus,
  setCompassRequestStatus,
}: GyroscopeControlProps) {
  useEffect(() => {
    if (typeof DeviceMotionEvent.requestPermission !== "function") {
      setCompassRequestStatus("granted");
      return;
    }
  }, []);

  function handleClick() {
    DeviceOrientationEvent.requestPermission().then(
      (orientationPermission: string) => {
        if (orientationPermission === "granted") {
          setCompassRequestStatus("granted");
        } else {
          setCompassRequestStatus("revoked");
        }
      },
    );
  }

  return (
    <Control prepend position="topleft">
      <Button
        $hide={compassRequestStatus !== "idle"}
        className="leaflet-bar"
        onClick={() => handleClick()}
        $src={gyroscopeIconSrc}
      ></Button>
    </Control>
  );
}

const Button = styled.div<{ $hide?: boolean; $src?: string }>`
  color: "inherit";
  aspect-ratio: 1/1;
  width: 34px;
  justify-content: center;
  align-items: center;
  padding: 2px;
  display: ${(props) => (props.$hide ? "none" : "grid")};
  background-image: url("${(props) => props.$src}");
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  background-color: white;
`;

export default GyroscopeControl;
