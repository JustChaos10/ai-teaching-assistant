import React, { useRef, useLayoutEffect } from "react";
import { OrbitControls, useTexture } from "@react-three/drei";
import { useThree } from "@react-three/fiber";
import { Avatar } from "./Avatar";

// ✅ Import the file since it's in src/components (not /public)
import classroomUrl from "./classroom.jpg";

function Backdrop() {
  const tex = useTexture(classroomUrl);
  const plane = useRef();
  const { camera, size } = useThree();

  useLayoutEffect(() => {
    // Distance behind the avatar
    const distance = 35;
    const vFov = (camera.fov * Math.PI) / 180;
    const height = 2 * Math.tan(vFov / 2) * distance;
    const width = height * camera.aspect;

    if (plane.current) {
      plane.current.scale.set(width, height, 1);
      // Adjust Y to taste to center behind head/torso
      plane.current.position.set(0, 1.2, -distance);
    }
  }, [camera, size]);

  return (
    <mesh ref={plane}>
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial map={tex} toneMapped={false} />
    </mesh>
  );
}

export function Experience({ audioUrl, phonemes }) {
  return (
    <>
      {/* 🏫 Background image plane */}
      <Backdrop />

      {/* 💡 Lights */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={1.2} />

      {/* 🎥 Camera controls */}
      <OrbitControls
        enableZoom
        enablePan
        enableDamping
        dampingFactor={0.08}
        minDistance={0.1}
        maxDistance={5}
        maxPolarAngle={Math.PI * 0.55}
        minPolarAngle={Math.PI * 0.2}
      />

      {/* 🧑‍🏫 Avatar slightly in front of backdrop */}
      <Avatar position={[0, -1.2, 0.5]} scale={1.05} audioUrl={audioUrl} phonemes={phonemes} />
    </>
  );
}
