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
    if (!window.DeviceMotionEvent) {
      setCompassRequestStatus("denied");
    } else if (!typeof window.DeviceMotionEvent.requestPermission) {
      setCompassRequestStatus("granted");
    }
  }, []);

  function handleClick() {
    DeviceOrientationEvent.requestPermission().then(
      (orientationPermission: string) => {
        setCompassRequestStatus(orientationPermission);
      },
    );
  }

  return (
    <Control prepend position="topleft">
      <Button
        className="leaflet-bar"
        onClick={() => handleClick()}
        $src={gyroscopeIconSrc}
        $isDisplayed={
          window.DeviceMotionEvent &&
          window.DeviceMotionEvent.requestPermission &&
          compassRequestStatus === "idle"
        }
      ></Button>
    </Control>
  );
}

const Button = styled.div<{ $isDisplayed?: boolean; $src?: string }>`
  color: "inherit";
  aspect-ratio: 1/1;
  width: 34px;
  justify-content: center;
  align-items: center;
  padding: 2px;
  display: ${({ $isDisplayed }) => ($isDisplayed ? "grid" : "none")};
  background-image: url("${({ $src }) => $src}");
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  background-color: white;
  cursor: pointer;
`;

export default GyroscopeControl;
