'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { useCruxStore, GraphNode, GraphLink } from '@/lib/store';
import { Slider } from '@/components/ui/slider';
import { DEMO_MODE, DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS } from '@/lib/demo-data';

// Dynamically import React Force Graph to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
});

function parseTimeOffset(timeOffset: string): number {
  // Parse T+HH:MM format to minutes
  const match = timeOffset.match(/T\+(\d{2}):(\d{2})/);
  if (!match) return 0;
  const hours = parseInt(match[1], 10);
  const minutes = parseInt(match[2], 10);
  return hours * 60 + minutes;
}

function formatTimeOffset(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `T+${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

export default function DigitalTwinGraph() {
  const {
    graphNodes,
    graphLinks,
    graphTimeOffset,
    setGraphTimeOffset,
    injects,
    selectedInjectId,
    highlightedNodeId,
    setHighlightedNode,
    setGraphData,
  } = useCruxStore();
  const graphRef = useRef<any>(null);
  const [graphReady, setGraphReady] = useState(false);
  const [showLegend, setShowLegend] = useState(true);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Demo-Mode: Lade hardcoded Daten beim ersten Render
  useEffect(() => {
    if (DEMO_MODE && graphNodes.length === 0) {
      setGraphData(DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS);
    }
    if (DEMO_MODE || graphNodes.length > 0) {
      setGraphReady(true);
    }
  }, [DEMO_MODE, graphNodes.length, setGraphData]);

  // Verwende Demo-Daten wenn Demo-Mode aktiv
  const displayNodes = DEMO_MODE ? DEMO_GRAPH_NODES : graphNodes;
  const displayLinks = DEMO_MODE ? DEMO_GRAPH_LINKS : graphLinks;

  // Calculate time range from injects
  const timeRange = injects.length > 0
    ? {
        min: 0,
        max: Math.max(...injects.map((inj) => parseTimeOffset(inj.time_offset))),
      }
    : { min: 0, max: 60 };

  const currentTimeMinutes = parseTimeOffset(graphTimeOffset);

  // Filter nodes/links based on current time and type filter
  const filteredNodes = displayNodes
    .filter((node) => !filterType || node.type === filterType)
    .map((node) => {
      // Check if node is compromised at current time
      const relevantInjects = injects.filter(
        (inj) =>
          parseTimeOffset(inj.time_offset) <= currentTimeMinutes &&
          inj.affected_assets.includes(node.id)
      );
      
      let status = node.status;
      if (relevantInjects.length > 0) {
        // Check if any inject indicates compromise
        const compromised = relevantInjects.some(
          (inj) => inj.content.toLowerCase().includes('compromised') ||
                   inj.content.toLowerCase().includes('encrypted') ||
                   inj.content.toLowerCase().includes('breach')
        );
        status = compromised ? 'compromised' : 'degraded';
      }

      return { ...node, status };
    });

  // Filter links based on filtered nodes
  const filteredLinks = displayLinks.filter(
    (link) =>
      filteredNodes.some((n) => n.id === link.source) &&
      filteredNodes.some((n) => n.id === link.target)
  );

  const nodeColor = (node: GraphNode & { status?: string }) => {
    // Highlight hovered/selected node
    if (highlightedNodeId === node.id) {
      return '#7F5AF0'; // Neural Violet for highlight (Spec)
    }
    
    // Spezieller Fall: Nicht-existierender Knoten (Halluzination)
    if (node.id === 'SRV-PAY-99' || node.id.includes('-99')) {
      return '#E53170'; // Intervention Red (Spec)
    }
    
    switch (node.status) {
      case 'compromised':
        return '#E53170'; // Intervention Red (Spec)
      case 'degraded':
        return '#D29922'; // Warning Amber
      case 'offline':
        return '#8B949E'; // Grey (transparent effect via opacity)
      case 'online':
        return '#2CB67D'; // Symbolic Green (Spec)
      default:
        return '#7F5AF0'; // Neural Violet (Spec)
    }
  };
  
  // Node-Icon basierend auf Typ
  const getNodeIcon = (node: GraphNode & { status?: string }) => {
    const size = highlightedNodeId === node.id ? 20 : 16;
    const color = nodeColor(node);
    
    switch (node.type) {
      case 'server':
        return (
          <g>
            <rect x={-size/2} y={-size/2} width={size} height={size} fill={color} opacity={0.2} />
            <rect x={-size/2} y={-size/2} width={size} height={size} fill="none" stroke={color} strokeWidth={2} />
            <line x1={-size/3} y1={0} x2={size/3} y2={0} stroke={color} strokeWidth={1.5} />
            <line x1={0} y1={-size/3} x2={0} y2={size/3} stroke={color} strokeWidth={1.5} />
          </g>
        );
      case 'database':
        return (
          <g>
            <ellipse cx={0} cy={0} rx={size/2} ry={size/3} fill={color} opacity={0.2} />
            <ellipse cx={0} cy={0} rx={size/2} ry={size/3} fill="none" stroke={color} strokeWidth={2} />
            <line x1={-size/3} y1={0} x2={size/3} y2={0} stroke={color} strokeWidth={1.5} />
          </g>
        );
      case 'network':
        return (
          <g>
            <polygon points={`0,-${size/2} ${size/2},0 0,${size/2} -${size/2},0`} fill={color} opacity={0.2} />
            <polygon points={`0,-${size/2} ${size/2},0 0,${size/2} -${size/2},0`} fill="none" stroke={color} strokeWidth={2} />
          </g>
        );
      default:
        return <circle r={size/2} fill={color} opacity={0.3} stroke={color} strokeWidth={2} />;
    }
  };

  const nodeOpacity = (node: GraphNode & { status?: string }) => {
    return node.status === 'offline' ? 0.3 : 1.0;
  };

  // Highlight selected node - Camera Fly-To Animation
  useEffect(() => {
    if (selectedInjectId && graphRef.current && graphReady) {
      const inject = injects.find((inj) => inj.inject_id === selectedInjectId);
      if (inject && inject.affected_assets.length > 0) {
        const nodeId = inject.affected_assets[0];
        const node = displayNodes.find((n) => n.id === nodeId);
        if (node) {
          const x = node.x ?? 0;
          const y = node.y ?? 0;
          graphRef.current.centerAt(x, y, 1000);
          graphRef.current.zoom(2.5, 1000);
        }
      }
    }
  }, [selectedInjectId, injects, displayNodes, graphReady]);

  // Highlight hovered node - Camera Fly-To
  useEffect(() => {
    if (highlightedNodeId && graphRef.current && graphReady) {
      const node = displayNodes.find((n) => n.id === highlightedNodeId);
      if (node) {
        const x = node.x ?? 0;
        const y = node.y ?? 0;
        graphRef.current.centerAt(x, y, 800);
        graphRef.current.zoom(2, 800);
      }
    }
  }, [highlightedNodeId, displayNodes, graphReady]);

  const nodeTypes = ['server', 'database', 'network', 'workstation'];
  const statusColors = [
    { status: 'online', color: '#2CB67D', label: 'Online' },
    { status: 'compromised', color: '#E53170', label: 'Compromised' },
    { status: 'degraded', color: '#D29922', label: 'Degraded' },
    { status: 'offline', color: '#8B949E', label: 'Offline' },
  ];

  const handleZoom = (delta: number) => {
    if (graphRef.current) {
      const newZoom = Math.max(0.5, Math.min(3, zoomLevel + delta));
      setZoomLevel(newZoom);
      graphRef.current.zoom(newZoom / zoomLevel, 300);
    }
  };

  const handleResetView = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400, 20);
      setZoomLevel(1);
    }
  };

  return (
    <div className="flex h-full flex-col bg-[#090C10]">
      <div className="border-b border-[#30363D] p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-[#E6EDF3]">Digital Twin / Knowledge Graph</h2>
            <p className="text-sm text-[#8B949E]">Ground Truth - Systemzustand zum Zeitpunkt</p>
          </div>
          <div className="flex items-center gap-2">
            {/* Zoom Controls */}
            <div className="flex items-center gap-1 rounded border border-[#30363D] bg-[#161B22] p-1">
              <button
                onClick={() => handleZoom(-0.2)}
                className="px-2 py-1 text-sm text-[#E6EDF3] hover:bg-[#30363D] rounded"
                title="Zoom Out"
              >
                −
              </button>
              <span className="px-2 py-1 text-xs text-[#8B949E] font-data">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={() => handleZoom(0.2)}
                className="px-2 py-1 text-sm text-[#E6EDF3] hover:bg-[#30363D] rounded"
                title="Zoom In"
              >
                +
              </button>
              <button
                onClick={handleResetView}
                className="px-2 py-1 text-xs text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D] rounded"
                title="Reset View"
              >
                Reset
              </button>
            </div>
            {/* Filter Dropdown */}
            <select
              value={filterType || ''}
              onChange={(e) => setFilterType(e.target.value || null)}
              className="rounded border border-[#30363D] bg-[#161B22] px-3 py-1 text-sm text-[#E6EDF3]"
            >
              <option value="">Alle Typen</option>
              {nodeTypes.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
            {/* Legend Toggle */}
            <button
              onClick={() => setShowLegend(!showLegend)}
              className="rounded border border-[#30363D] bg-[#161B22] px-3 py-1 text-xs text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D]"
            >
              {showLegend ? 'Legende ▼' : 'Legende ▶'}
            </button>
          </div>
        </div>
        {/* Legend */}
        {showLegend && (
          <div className="mt-4 flex flex-wrap gap-4 rounded border border-[#30363D] bg-[#161B22] p-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[#8B949E]">Status:</span>
              {statusColors.map(({ status, color, label }) => (
                <div key={status} className="flex items-center gap-1">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs text-[#E6EDF3]">{label}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2 border-l border-[#30363D] pl-4">
              <span className="text-xs font-semibold text-[#8B949E]">Links:</span>
              <div className="flex items-center gap-1">
                <div className="h-0.5 w-6 bg-[#7F5AF0]" />
                <span className="text-xs text-[#E6EDF3]">Security</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="h-0.5 w-6 bg-[#2CB67D]" />
                <span className="text-xs text-[#E6EDF3]">Data Flow</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="h-0.5 w-6 bg-[#D29922]" />
                <span className="text-xs text-[#E6EDF3]">Replication</span>
              </div>
            </div>
            <div className="flex items-center gap-2 border-l border-[#30363D] pl-4">
              <span className="text-xs font-semibold text-[#8B949E]">Nodes:</span>
              <span className="text-xs text-[#E6EDF3]">{filteredNodes.length} / {displayNodes.length}</span>
              <span className="text-xs text-[#8B949E]">•</span>
              <span className="text-xs text-[#E6EDF3]">{filteredLinks.length} Links</span>
            </div>
          </div>
        )}
      </div>
      <div className="relative flex-1">
        {!graphReady && displayNodes.length === 0 ? (
          <div className="flex h-full items-center justify-center text-[#8B949E]">
            <div className="text-center">
              <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-[#7F5AF0] border-t-transparent mx-auto" />
              <p className="text-sm">Lade Digital Twin...</p>
            </div>
          </div>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={{ nodes: filteredNodes, links: filteredLinks }}
            nodeLabel={(node: any) => {
              const status = node.status || 'unknown';
              const connections = filteredLinks.filter(
                (l: any) => l.source === node.id || l.target === node.id
              ).length;
              return `${node.label}\n(${node.id})\nStatus: ${status}\nConnections: ${connections}`;
            }}
            nodeColor={(node: any) => {
              const color = nodeColor(node as GraphNode & { status?: string });
              const opacity = nodeOpacity(node as GraphNode & { status?: string });
              // Konvertiere Hex zu RGBA für Opacity
              if (opacity < 1.0 && color.startsWith('#')) {
                const r = parseInt(color.slice(1, 3), 16);
                const g = parseInt(color.slice(3, 5), 16);
                const b = parseInt(color.slice(5, 7), 16);
                return `rgba(${r}, ${g}, ${b}, ${opacity})`;
              }
              return color;
            }}
            nodeVal={(node: any) => {
              if (highlightedNodeId === node.id) return 20;
              if (node.id === 'SRV-PAY-99') return 15; // Größer für Halluzination
              
              // Node-Größe basierend auf Typ
              const baseSize = 10;
              switch (node.type) {
                case 'network':
                  return baseSize + 4; // Firewalls/Load Balancer größer
                case 'server':
                  return baseSize + 2;
                case 'database':
                  return baseSize + 3;
                case 'workstation':
                  return baseSize;
                default:
                  return baseSize;
              }
            }}
            nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
              const label = node.label || node.id;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px Inter`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              const color = nodeColor(node as GraphNode & { status?: string });
              ctx.fillStyle = color;
              ctx.fillText(label, node.x || 0, (node.y || 0) + 20);
            }}
            linkColor={(link: any) => {
              // Farbcodierung basierend auf Link-Typ - HELLERE FARBEN für bessere Sichtbarkeit
              switch (link.type) {
                case 'PROTECTS':
                case 'ROUTES_TO':
                  return '#7F5AF0'; // Violett für Security-Links
                case 'USES':
                case 'CALLS':
                  return '#2CB67D'; // Grün für Datenfluss
                case 'REPLICATES_TO':
                  return '#D29922'; // Gelb für Replication
                case 'DISTRIBUTES_TO':
                  return '#7F5AF0'; // Violett für Load Balancing
                case 'CONNECTS_TO':
                  return '#2CB67D'; // Grün für Verbindungen
                case 'PEER_TO_PEER':
                  return '#8B949E'; // Grau für Peer-Verbindungen
                default:
                  return '#484F58'; // Helleres Grau statt sehr dunkel
              }
            }}
            linkWidth={(link: any) => {
              // DEUTLICH DICKERE LINKS für bessere Sichtbarkeit
              switch (link.type) {
                case 'PROTECTS':
                case 'ROUTES_TO':
                  return 3; // Sehr dick für Security
                case 'DISTRIBUTES_TO':
                  return 2.5; // Dick für Load Balancing
                case 'USES':
                case 'CALLS':
                  return 2.5; // Dick für Datenfluss
                case 'REPLICATES_TO':
                  return 2; // Mittel für Replication
                default:
                  return 2; // Mindestens 2px für alle Links
              }
            }}
            linkLabel={(link: any) => link.type}
            linkDirectionalArrowLength={10}
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowColor={(link: any) => {
              // Pfeil-Farbe passt sich Link-Farbe an
              switch (link.type) {
                case 'PROTECTS':
                case 'ROUTES_TO':
                case 'DISTRIBUTES_TO':
                  return '#7F5AF0';
                case 'USES':
                case 'CALLS':
                case 'CONNECTS_TO':
                  return '#2CB67D';
                case 'REPLICATES_TO':
                  return '#D29922';
                default:
                  return '#484F58';
              }
            }}
            linkDirectionalParticles={(link: any) => {
              // Partikel für alle aktiven Links
              return link.type === 'USES' || link.type === 'CALLS' || link.type === 'CONNECTS_TO' ? 3 : 0;
            }}
            linkDirectionalParticleSpeed={0.015}
            linkDirectionalParticleWidth={3}
            linkDirectionalParticleColor={() => '#2CB67D'}
            // Physik-Fix: Stabileres Layout
            warmupTicks={100}
            cooldownTicks={0}
            onEngineStop={() => {
              // Graph ist stabilisiert
              setGraphReady(true);
            }}
            onNodeHover={(node: any) => {
              if (node) {
                setHighlightedNode(node.id);
              } else {
                setHighlightedNode(null);
              }
            }}
            onNodeClick={(node: any) => {
              if (node && graphRef.current) {
                const x = node.x || 0;
                const y = node.y || 0;
                graphRef.current.centerAt(x, y, 800);
                graphRef.current.zoom(2, 800);
                setZoomLevel(2);
              }
            }}
            onBackgroundClick={() => {
              setHighlightedNode(null);
              handleResetView();
            }}
            backgroundColor="#090C10"
            width={800}
            height={600}
          />
        )}
      </div>
      <div className="border-t border-[#30363D] p-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-[#8B949E]">Zeitpunkt</span>
            <span className="font-data text-[#E6EDF3]">{graphTimeOffset}</span>
          </div>
          <Slider
            value={[currentTimeMinutes]}
            min={timeRange.min}
            max={timeRange.max || 60}
            step={1}
            onValueChange={([value]) => {
              setGraphTimeOffset(formatTimeOffset(value));
            }}
            className="w-full"
          />
        </div>
      </div>
    </div>
  );
}

