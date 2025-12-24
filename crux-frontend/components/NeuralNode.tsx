'use client';

import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { GraphNode } from '@/lib/store';
import { 
  Server, 
  Database, 
  Network, 
  Monitor,
  AlertCircle,
  CheckCircle2,
  XCircle,
  AlertTriangle
} from 'lucide-react';

interface NeuralNodeData extends GraphNode {
  status?: 'online' | 'offline' | 'compromised' | 'degraded';
  criticality?: 'critical' | 'high' | 'standard';
  isHighlighted?: boolean;
  isHovered?: boolean;
  isInBlastRadius?: boolean; // Für Blast Radius Hover
  isGhosted?: boolean; // Für Time-Travel Ghosting
  fogOfWar?: 'unknown' | 'alert' | 'confirmed' | 'normal'; // Fog of War Status
}

const NeuralNode = ({ data, selected }: NodeProps<NeuralNodeData>) => {
  const { 
    id, 
    label, 
    type, 
    status = 'online', 
    criticality = 'standard',
    isHighlighted = false, 
    isHovered = false,
    isInBlastRadius = false,
    isGhosted = false,
    fogOfWar,
  } = data;
  
  // Fog of War: Anpasse visuelle Darstellung basierend auf verfügbaren Informationen
  const fogOpacity = fogOfWar === 'unknown' ? 0.3 : fogOfWar === 'alert' ? 0.6 : 1.0;
  const fogBorderStyle = fogOfWar === 'unknown' ? 'dashed' : fogOfWar === 'alert' ? 'dotted' : 'solid';
  
  // Status-Farben basierend auf CRUX Design System
  const statusConfig: Record<string, {
    color: string;
    bgColor: string;
    haloColor: string;
    icon: typeof CheckCircle2;
    pulse: boolean;
  }> = {
    online: {
      color: '#2CB67D', // Symbolic Green
      bgColor: 'rgba(44, 182, 125, 0.15)',
      haloColor: 'rgba(44, 182, 125, 0.4)',
      icon: CheckCircle2,
      pulse: false,
    },
    compromised: {
      color: '#E53170', // Intervention Red
      bgColor: 'rgba(229, 49, 112, 0.2)',
      haloColor: 'rgba(229, 49, 112, 0.6)',
      icon: XCircle,
      pulse: true,
    },
    degraded: {
      color: '#D29922', // Warning Amber
      bgColor: 'rgba(210, 153, 34, 0.15)',
      haloColor: 'rgba(210, 153, 34, 0.4)',
      icon: AlertTriangle,
      pulse: false,
    },
    offline: {
      color: '#8B949E', // Grey
      bgColor: 'rgba(139, 148, 158, 0.1)',
      haloColor: 'rgba(139, 148, 158, 0.2)',
      icon: AlertCircle,
      pulse: false,
    },
    // Fallback für unbekannte Status-Werte
    unknown: {
      color: '#8B949E', // Grey
      bgColor: 'rgba(139, 148, 158, 0.1)',
      haloColor: 'rgba(139, 148, 158, 0.2)',
      icon: AlertCircle,
      pulse: false,
    },
  };

  // Normalisiere Status (lowercase) und verwende Fallback
  const normalizedStatus = (status || 'online').toLowerCase() as keyof typeof statusConfig;
  const config = statusConfig[normalizedStatus] || statusConfig.unknown;
  const IconComponent = config.icon;
  const isCompromised = status === 'compromised';
  const isSelected = selected || isHighlighted;

  // Icon basierend auf Asset-Typ
  const getTypeIcon = () => {
    const iconSize = 24;
    const iconColor = config.color;
    
    switch (type) {
      case 'server':
        return <Server size={iconSize} color={iconColor} strokeWidth={2} />;
      case 'database':
        return <Database size={iconSize} color={iconColor} strokeWidth={2} />;
      case 'network':
        return <Network size={iconSize} color={iconColor} strokeWidth={2} />;
      case 'workstation':
        return <Monitor size={iconSize} color={iconColor} strokeWidth={2} />;
      default:
        return <Server size={iconSize} color={iconColor} strokeWidth={2} />;
    }
  };

  // Criticality Halo - Pulsating Ring für Critical Assets
  const criticalityHalo = criticality === 'critical' ? (
    <div className="neural-node-criticality-halo criticality-critical" />
  ) : criticality === 'high' ? (
    <div className="neural-node-criticality-halo criticality-high" />
  ) : null;

  const nodeOpacity = isGhosted ? 0.3 : (isInBlastRadius ? 1 : 1);

  return (
    <div className="neural-node-wrapper" style={{ opacity: nodeOpacity }}>
      {/* Criticality Halo - Äußerer Ring für Critical Assets */}
      {criticalityHalo}
      
      {/* Status Halo - Glowing Ring */}
      <div
        className={`neural-node-halo ${config.pulse ? 'pulse-error' : ''} ${isSelected ? 'halo-highlight' : ''}`}
        style={{
          '--halo-color': config.haloColor,
        } as React.CSSProperties}
      />
      
      {/* Node Card */}
      <div
        className={`neural-node-card ${isCompromised ? 'glitch pulse-red' : ''} ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''} ${criticality === 'critical' ? 'critical-asset' : ''} ${criticality === 'high' ? 'high-asset' : ''} ${fogOfWar === 'unknown' ? 'fog-unknown' : ''}`}
        style={{
          backgroundColor: config.bgColor,
          borderColor: config.color,
          borderWidth: criticality === 'critical' ? '3px' : criticality === 'high' ? '2px' : '2px',
          borderStyle: fogBorderStyle,
          opacity: fogOpacity,
          boxShadow: isCompromised
            ? `0 0 20px ${config.haloColor}, 0 0 40px ${config.haloColor}`
            : isSelected 
              ? `0 0 20px ${config.haloColor}, 0 0 40px ${config.haloColor}` 
              : `0 0 10px ${config.haloColor}`,
        }}
      >
        {/* Status Badge oben rechts */}
        <div
          className="neural-node-status-badge"
          style={{
            backgroundColor: config.color,
          }}
        >
          <IconComponent size={10} color="#FFFFFF" strokeWidth={2.5} />
        </div>

        {/* Asset Icon */}
        <div className="neural-node-icon">
          {getTypeIcon()}
        </div>

        {/* Label in Monospace unter dem Icon */}
        <div className="neural-node-label">
          <div className="neural-node-label-text" style={{ color: config.color }}>
            {label}
          </div>
          <div className="neural-node-label-id" style={{ color: '#8B949E' }}>
            {id}
          </div>
        </div>

        {/* React Flow Handles für Verbindungen */}
        <Handle
          type="target"
          position={Position.Top}
          style={{
            background: config.color,
            width: 8,
            height: 8,
            border: `2px solid #FFFFFF`,
          }}
        />
        <Handle
          type="source"
          position={Position.Bottom}
          style={{
            background: config.color,
            width: 8,
            height: 8,
            border: `2px solid #FFFFFF`,
          }}
        />
        <Handle
          type="target"
          position={Position.Left}
          style={{
            background: config.color,
            width: 8,
            height: 8,
            border: `2px solid #FFFFFF`,
          }}
        />
        <Handle
          type="source"
          position={Position.Right}
          style={{
            background: config.color,
            width: 8,
            height: 8,
            border: `2px solid #FFFFFF`,
          }}
        />
      </div>

      <style jsx>{`
        .neural-node-wrapper {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .neural-node-halo {
          position: absolute;
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: radial-gradient(circle, var(--halo-color) 0%, transparent 70%);
          opacity: 0.6;
          animation: pulse-halo 3s ease-in-out infinite;
          pointer-events: none;
        }

        .neural-node-halo.pulse-error {
          animation: pulse-error-halo 1.5s ease-in-out infinite;
        }

        .neural-node-halo.halo-highlight {
          width: 140px;
          height: 140px;
          opacity: 0.8;
        }

        .neural-node-card {
          position: relative;
          width: 100px;
          min-height: 100px;
          border-radius: 12px;
          border: 2px solid;
          padding: 12px 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: all 0.3s ease;
          backdrop-filter: blur(10px);
          background: rgba(255, 255, 255, 0.95);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .neural-node-card:hover {
          transform: scale(1.05);
          z-index: 10;
        }

        .neural-node-card.selected {
          transform: scale(1.1);
          z-index: 20;
        }

        .neural-node-card.glitch {
          animation: glitch 0.3s infinite;
        }

        .neural-node-status-badge {
          position: absolute;
          top: -6px;
          right: -6px;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px solid #FFFFFF;
          z-index: 5;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .neural-node-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          margin-top: 4px;
        }

        .neural-node-label {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
          margin-top: 4px;
        }

        .neural-node-label-text {
          font-family: 'JetBrains Mono', 'Courier New', monospace;
          font-size: 11px;
          font-weight: 600;
          text-align: center;
          line-height: 1.2;
          max-width: 90px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          color: #1A202C;
        }

        .neural-node-label-id {
          font-family: 'JetBrains Mono', 'Courier New', monospace;
          font-size: 9px;
          text-align: center;
          opacity: 0.7;
          color: #4A5568;
        }

        @keyframes pulse-halo {
          0%, 100% {
            opacity: 0.4;
            transform: scale(1);
          }
          50% {
            opacity: 0.7;
            transform: scale(1.1);
          }
        }

        @keyframes pulse-error-halo {
          0%, 100% {
            opacity: 0.6;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }

        @keyframes glitch {
          0% {
            transform: translate(0);
          }
          20% {
            transform: translate(-2px, 2px);
          }
          40% {
            transform: translate(-2px, -2px);
          }
          60% {
            transform: translate(2px, 2px);
          }
          80% {
            transform: translate(2px, -2px);
          }
          100% {
            transform: translate(0);
          }
        }

        .neural-node-card.critical-asset {
          border-style: double;
          border-width: 3px;
        }

        .neural-node-card.high-asset {
          border-style: solid;
          border-width: 2px;
        }

        .neural-node-criticality-halo {
          position: absolute;
          width: 140px;
          height: 140px;
          border-radius: 50%;
          pointer-events: none;
          animation: pulse-criticality 2s ease-in-out infinite;
        }

        .neural-node-criticality-halo.criticality-critical {
          border: 3px solid rgba(229, 49, 112, 0.6);
          box-shadow: 0 0 20px rgba(229, 49, 112, 0.4);
        }

        .neural-node-criticality-halo.criticality-high {
          border: 2px solid rgba(210, 153, 34, 0.5);
          box-shadow: 0 0 15px rgba(210, 153, 34, 0.3);
        }

        @keyframes pulse-criticality {
          0%, 100% {
            opacity: 0.6;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.1);
          }
        }
      `}</style>
    </div>
  );
};

export default memo(NeuralNode);

