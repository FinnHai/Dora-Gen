'use client';

import { useMemo } from 'react';
import { Node } from 'reactflow';
import { TopologyLayer } from '@/lib/layered-topology';

interface LayerBackgroundProps {
  nodes: Node[];
  width: number;
  height: number;
  affectedLayers?: Set<TopologyLayer>;
}

/**
 * Layer Background: Zeigt semantische Schichten als Hintergrund-Panels
 * 
 * Macht die Architektur-Schichten visuell deutlich und zeigt,
 * welche Schichten von einem Angriff betroffen sind.
 */
export default function LayerBackground({
  nodes,
  width,
  height,
  affectedLayers = new Set(),
}: LayerBackgroundProps) {
  const layerConfigs = useMemo(() => {
    const layerHeights = {
      external: height * 0.25,
      application: height * 0.4,
      data: height * 0.25,
      other: height * 0.1,
    };

    return [
      {
        layer: 'external' as TopologyLayer,
        label: 'External / DMZ',
        y: 0,
        height: layerHeights.external,
        color: 'rgba(127, 90, 240, 0.1)', // Neural Violet
        borderColor: 'rgba(127, 90, 240, 0.3)',
        isAffected: affectedLayers.has('external'),
      },
      {
        layer: 'application' as TopologyLayer,
        label: 'Application Layer',
        y: layerHeights.external,
        height: layerHeights.application,
        color: 'rgba(44, 182, 125, 0.1)', // Symbolic Green
        borderColor: 'rgba(44, 182, 125, 0.3)',
        isAffected: affectedLayers.has('application'),
      },
      {
        layer: 'data' as TopologyLayer,
        label: 'Data Layer',
        y: layerHeights.external + layerHeights.application,
        height: layerHeights.data,
        color: 'rgba(229, 49, 112, 0.1)', // Intervention Red
        borderColor: 'rgba(229, 49, 112, 0.3)',
        isAffected: affectedLayers.has('data'),
      },
    ];
  }, [height, affectedLayers]);

  return (
    <div className="absolute inset-0 pointer-events-none" style={{ width, height }}>
      {layerConfigs.map((config) => (
        <div
          key={config.layer}
          className="absolute left-0 right-0 transition-all duration-500"
          style={{
            top: `${(config.y / height) * 100}%`,
            height: `${(config.height / height) * 100}%`,
            backgroundColor: config.isAffected
              ? 'rgba(229, 49, 112, 0.15)'
              : config.color,
            borderTop: `1px solid ${config.borderColor}`,
            borderBottom: `1px solid ${config.borderColor}`,
            // KEIN backdrop-filter hier - würde Nodes unscharf machen!
          }}
        >
          {/* Layer Label */}
          <div
            className="absolute left-4 top-2 text-xs font-semibold font-data"
            style={{
              color: config.isAffected ? '#E53170' : '#8B949E',
            }}
          >
            {config.label}
            {config.isAffected && ' ⚠️ ATTACKED'}
          </div>
        </div>
      ))}
    </div>
  );
}

