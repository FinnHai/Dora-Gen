'use client';

import { memo } from 'react';
import { EdgeProps, getBezierPath } from 'reactflow';
import { GraphLink } from '@/lib/store';

interface NeuralEdgeData extends GraphLink {
  isCompromised?: boolean;
}

const NeuralEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: EdgeProps<NeuralEdgeData>) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const { type, isCompromised = false } = data || {};

  // Link-Farben basierend auf Typ
  const getLinkColor = () => {
    switch (type) {
      case 'PROTECTS':
      case 'ROUTES_TO':
      case 'DISTRIBUTES_TO':
        return isCompromised ? '#E53170' : '#7F5AF0'; // Neural Violet / Intervention Red
      case 'USES':
      case 'CALLS':
      case 'CONNECTS_TO':
        return isCompromised ? '#E53170' : '#2CB67D'; // Symbolic Green / Intervention Red
      case 'REPLICATES_TO':
        return isCompromised ? '#E53170' : '#D29922'; // Warning Amber / Intervention Red
      case 'PEER_TO_PEER':
        return isCompromised ? '#E53170' : '#8B949E'; // Grey / Intervention Red
      default:
        return isCompromised ? '#E53170' : '#484F58';
    }
  };

  const linkColor = getLinkColor();
  const linkWidth = isCompromised ? 3 : 2;
  
  // Opacity aus style prop oder Standard-Wert
  const finalOpacity = style.opacity !== undefined ? style.opacity : (isCompromised ? 1 : 0.8);

  return (
    <>
      {/* Unsichtbarer Pfad für animateMotion Referenz */}
      <path
        id={`${id}-motion-path`}
        d={edgePath}
        fill="none"
        stroke="none"
        style={{ visibility: 'hidden' }}
      />
      
      {/* Hauptverbindungslinie */}
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        fill="none"
        stroke={linkColor}
        strokeWidth={linkWidth}
        strokeDasharray={type === 'PEER_TO_PEER' ? '5,5' : '0'}
        opacity={finalOpacity}
      />
      
      {/* Animierte Traffic-Partikel */}
      {!isCompromised && (
        <g>
          <circle r="3" fill={linkColor}>
            <animateMotion
              dur="3s"
              repeatCount="indefinite"
            >
              <mpath href={`#${id}-motion-path`} />
            </animateMotion>
          </circle>
          <circle r="2.5" fill={linkColor} opacity="0.7">
            <animateMotion
              dur="4s"
              repeatCount="indefinite"
              begin="1s"
            >
              <mpath href={`#${id}-motion-path`} />
            </animateMotion>
          </circle>
          <circle r="2" fill={linkColor} opacity="0.5">
            <animateMotion
              dur="5s"
              repeatCount="indefinite"
              begin="2s"
            >
              <mpath href={`#${id}-motion-path`} />
            </animateMotion>
          </circle>
        </g>
      )}

      {/* Compromised: Rote Partikel */}
      {isCompromised && (
        <g>
          <circle r="4" fill="#E53170">
            <animateMotion
              dur="2s"
              repeatCount="indefinite"
            >
              <mpath href={`#${id}-motion-path`} />
            </animateMotion>
            <animate
              attributeName="opacity"
              values="1;0.3;1"
              dur="2s"
              repeatCount="indefinite"
            />
          </circle>
          <circle r="3.5" fill="#E53170" opacity="0.8">
            <animateMotion
              dur="2.5s"
              repeatCount="indefinite"
              begin="0.5s"
            >
              <mpath href={`#${id}-motion-path`} />
            </animateMotion>
            <animate
              attributeName="opacity"
              values="0.8;0.2;0.8"
              dur="2.5s"
              repeatCount="indefinite"
            />
          </circle>
          <circle r="3" fill="#E53170" opacity="0.6">
            <animateMotion
              dur="3s"
              repeatCount="indefinite"
              begin="1s"
            >
              <mpath href={`#${id}-motion-path`} />
            </animateMotion>
            <animate
              attributeName="opacity"
              values="0.6;0.1;0.6"
              dur="3s"
              repeatCount="indefinite"
            />
          </circle>
        </g>
      )}

      {/* Pfeil-Marker wird automatisch von React Flow hinzugefügt */}
    </>
  );
};

export default memo(NeuralEdge);

