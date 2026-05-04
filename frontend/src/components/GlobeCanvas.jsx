import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LEVELS } from '../lib/constants';
import { motion } from 'framer-motion';

const latLongToVector3 = (lat, lon, radius) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
};

function GlobeInner({ currentLevel, isTransitioning, setIsTransitioning }) {
  const groupRef = useRef();
  
  // Calculate target rotation for the current level's longitude
  const targetRotationY = useMemo(() => {
    const levelData = LEVELS[currentLevel - 1];
    if (!levelData) return 0;
    // Target rotation needed to center the specific longitude
    // The globe is centered at lon=0. We rotate opposite to lon to bring it to center front.
    // Adds a 90-degree offset depending on camera start
    return (levelData.location.lon * Math.PI) / 180;
  }, [currentLevel]);

  useFrame((state, delta) => {
    if (groupRef.current) {
      if (isTransitioning) {
        // Rotate towards target quickly
        let currentRot = groupRef.current.rotation.y;
        let diff = targetRotationY - (currentRot % (Math.PI * 2));
        
        // Normalize diff to -PI to PI
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;

        groupRef.current.rotation.y += diff * delta * 2;
        
        if (Math.abs(diff) < 0.01) {
          setIsTransitioning(false);
        }
      } else {
        // Slow auto-rotation
        groupRef.current.rotation.y += 0.0008;
      }
    }
  });

  return (
    <group ref={groupRef}>
      {/* Base wireframe */}
      <mesh>
        <sphereGeometry args={[2.5, 48, 48]} />
        <meshBasicMaterial color="#1e1e1e" wireframe={true} transparent opacity={0.6} />
      </mesh>
      
      {/* Glow layer wireframe */}
      <mesh>
        <sphereGeometry args={[2.52, 48, 48]} />
        <meshBasicMaterial color="#2a2a2a" wireframe={true} transparent opacity={0.3} />
      </mesh>

      {/* Atmosphere Ring */}
      <mesh rotation={[23.5 * (Math.PI/180), 0, 0]}>
        <torusGeometry args={[2.6, 0.01, 16, 100]} />
        <meshBasicMaterial color="#7a7870" transparent opacity={0.15} />
      </mesh>

      {/* Crisis Markers */}
      {LEVELS.map((level, i) => {
        const isActive = currentLevel === level.id;
        const radiusOffset = 2.52;
        const pos = latLongToVector3(level.location.lat, level.location.lon, radiusOffset);
        
        return (
          <Marker 
            key={level.id} 
            position={pos} 
            isActive={isActive} 
          />
        );
      })}
    </group>
  );
}

function Marker({ position, isActive }) {
  const markerRef = useRef();
  
  useFrame((state) => {
    if (isActive && markerRef.current) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.3;
      markerRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <mesh ref={markerRef} position={position}>
      <sphereGeometry args={[isActive ? 0.05 : 0.03, 16, 16]} />
      <meshBasicMaterial color={isActive ? '#d68910' : '#3a3835'} />
    </mesh>
  );
}

export default function GlobeCanvas({ currentLevel = 1, onRotated }) {
  const [isTransitioning, setIsTransitioning] = React.useState(true);

  useEffect(() => {
    setIsTransitioning(true);
  }, [currentLevel]);

  useEffect(() => {
    if (!isTransitioning && onRotated) {
      const timer = setTimeout(onRotated, 1000); // give it a sec after locking
      return () => clearTimeout(timer);
    }
  }, [isTransitioning, onRotated]);

  return (
    <div style={{ width: '60vw', height: '60vh', pointerEvents: 'none' }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
        <GlobeInner 
          currentLevel={currentLevel} 
          isTransitioning={isTransitioning}
          setIsTransitioning={setIsTransitioning}
        />
      </Canvas>
    </div>
  );
}
