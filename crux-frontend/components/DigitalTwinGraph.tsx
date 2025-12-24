'use client';

import { useEffect, useCallback, useMemo, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useCruxStore, GraphNode, GraphLink } from '@/lib/store';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DEMO_MODE, DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS } from '@/lib/demo-data';
import { applySmartLayout, applyInitialScatter } from '@/lib/layout-utils';
import { applyHybridLayout } from '@/lib/force-layout';
import { useDigitalTwinData } from '@/hooks/useDigitalTwinData';
import { useScenarioReplay } from '@/hooks/useScenarioReplay';
import { useFogOfWar } from '@/hooks/useFogOfWar';
import { organizeLayeredTopology, calculateCascadingEffects, TopologyLayer } from '@/lib/layered-topology';
import { graphNodeToReactFlowNode, graphLinkToReactFlowEdge } from '@/lib/graphTransformer';
import NeuralNode from './NeuralNode';
import NeuralEdge from './NeuralEdge';
import CoherenceChart from './CoherenceChart';
import EvaluationDashboard from './EvaluationDashboard';
import ComplianceScore from './ComplianceScore';
import LayerBackground from './LayerBackground';
import ModeIndicator from './ModeIndicator';
import ForensicTimeline from './ForensicTimeline';
import DecisionPoint from './DecisionPoint';
import EvidenceMatrix from './EvidenceMatrix';
import ScenarioLoader from './ScenarioLoader';

// Custom Node und Edge Types registrieren
const nodeTypes = {
  neural: NeuralNode,
};

const edgeTypes = {
  neural: NeuralEdge,
};

function parseTimeOffset(timeOffset: string): number {
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
    graphTimeOffset,
    setGraphTimeOffset,
    selectedInjectId,
    highlightedNodeId,
    setHighlightedNode,
    currentScenarioId,
    viewMode,
    setViewMode,
    pendingDecision,
    setPendingDecision,
    interactiveMode,
  } = useCruxStore();

  const [showLegend, setShowLegend] = useState(true);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [isInitialLayout, setIsInitialLayout] = useState(true);

  // Daten-Hook: Verwaltet Topology und Timeline
  const {
    graphNodes: backendNodes,
    graphLinks: backendLinks,
    timelineEvents,
    mode,
    isLoading,
    error,
  } = useDigitalTwinData(currentScenarioId);

  // Scenario Replay: Wende Timeline Events auf Topology an (Ground Truth)
  const replayedNodes = useScenarioReplay(
    DEMO_MODE || backendNodes.length === 0 ? DEMO_GRAPH_NODES : backendNodes,
    timelineEvents,
    graphTimeOffset
  );

  // Fog of War: Berechne Perceived State basierend auf View Mode
  const perceivedNodes = useFogOfWar(
    replayedNodes,
    timelineEvents,
    graphTimeOffset,
    viewMode
  );

  // Verwende Demo-Daten wenn Demo-Mode aktiv ODER wenn keine Backend-Daten vorhanden
  // WICHTIG: Verwende perceivedNodes für Fog of War, replayedNodes für God Mode
  const baseNodes = (DEMO_MODE || backendNodes.length === 0) && DEMO_GRAPH_NODES.length > 0 
    ? DEMO_GRAPH_NODES 
    : perceivedNodes;
  
  const displayNodes = baseNodes;
  
  // WICHTIG: Verwende Demo-Links wenn Demo-Nodes verwendet werden, sonst Backend-Links
  // Dies stellt sicher, dass Links und Nodes zusammenpassen
  const displayLinks = useMemo(() => {
    const usingDemoNodes = (DEMO_MODE || backendNodes.length === 0) && DEMO_GRAPH_NODES.length > 0;
    
    // Wenn Demo-Nodes verwendet werden, verwende auch Demo-Links
    if (usingDemoNodes) {
      return DEMO_GRAPH_LINKS.length > 0 ? DEMO_GRAPH_LINKS : [];
    }
    
    // Wenn Backend-Nodes verwendet werden, verwende Backend-Links
    // WICHTIG: Stelle sicher, dass Links zu den aktuellen Nodes passen
    if (backendLinks.length > 0) {
      // Filtere Links die zu den aktuellen Nodes passen
      const nodeIds = new Set(displayNodes.map(n => n.id));
      const validLinks = backendLinks.filter(
        link => nodeIds.has(link.source) && nodeIds.has(link.target)
      );
      
      // Wenn keine validen Backend-Links vorhanden, verwende Demo-Links als Fallback
      if (validLinks.length === 0 && DEMO_GRAPH_LINKS.length > 0) {
        console.warn('⚠️ Keine gültigen Backend-Links gefunden, verwende Demo-Links als Fallback');
        return DEMO_GRAPH_LINKS;
      }
      
      return validLinks;
    }
    
    // Fallback: Verwende Demo-Links wenn verfügbar
    return DEMO_GRAPH_LINKS.length > 0 ? DEMO_GRAPH_LINKS : [];
  }, [DEMO_MODE, backendNodes.length, backendLinks, displayNodes]);

  const graphReady = !isLoading && displayNodes.length > 0;

  // Calculate time range from timeline events
  const timeRange = timelineEvents.length > 0
    ? {
        min: 0,
        max: Math.max(...timelineEvents.map((inj) => parseTimeOffset(inj.time_offset))),
      }
    : { min: 0, max: 60 };

  const currentTimeMinutes = parseTimeOffset(graphTimeOffset);

  // Helper-Funktion für Link-Farben
  const getLinkColor = (linkType: string, isCompromised: boolean): string => {
    if (isCompromised) return '#E53170';
    switch (linkType) {
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
      case 'PEER_TO_PEER':
        return '#8B949E';
      default:
        return '#484F58';
    }
  };

  // Berechne Cascading Effects für Layer Background
  const cascadingEffects = useMemo(() => {
    const compromisedNodeIds = new Set(
      displayNodes
        .filter(n => n.status === 'compromised')
        .map(n => n.id)
    );
    
    if (compromisedNodeIds.size === 0) {
      return { affectedLayers: new Set<TopologyLayer>(), attackPath: [] };
    }

    return calculateCascadingEffects(
      displayNodes.map(n => ({ id: n.id, data: n } as Node)),
      displayLinks.map(l => ({ source: l.source, target: l.target } as Edge)),
      compromisedNodeIds
    );
  }, [displayNodes, displayLinks]);

  // Konvertiere GraphNodes zu React Flow Nodes mit Layered Topology
  const reactFlowNodes: Node[] = useMemo(() => {
    const filteredNodes = displayNodes.filter(
      (node) => !filterType || filterType === 'all' || node.type === filterType
    );

    // Erstelle initial Nodes - Status wurde bereits durch useScenarioReplay berechnet
    let nodesWithStatus = filteredNodes.map((node) => {
      return graphNodeToReactFlowNode(node, {
        isHighlighted: highlightedNodeId === node.id,
        isHovered: hoveredNodeId === node.id,
        isInBlastRadius: false, // TODO: Implement Blast Radius
        isGhosted: false, // TODO: Implement Time-Travel Ghosting
      });
    });

    // Wende Layered Topology an wenn Initial Layout oder keine Positionen vorhanden
    const hasPositions = nodesWithStatus.some(n => n.position.x !== 0 || n.position.y !== 0);
    if (isInitialLayout || !hasPositions) {
      // Verwende Layered Topology für semantische Schichten
      const layoutedNodes = organizeLayeredTopology(
        nodesWithStatus,
        displayLinks.map(l => ({ source: l.source, target: l.target } as Edge)),
        { width: 1200, height: 800 }
      );
      nodesWithStatus = layoutedNodes;
    }

    return nodesWithStatus;
  }, [displayNodes, displayLinks, filterType, highlightedNodeId, hoveredNodeId, isInitialLayout]);

  // Konvertiere GraphLinks zu React Flow Edges mit Focus Mode Support
  const reactFlowEdges: Edge[] = useMemo(() => {
    const nodeIds = new Set(reactFlowNodes.map(n => n.id));
    
    // Debug: Log wenn Links gefiltert werden
    const totalLinks = displayLinks.length;
    const validLinks = displayLinks.filter(
      (link) => nodeIds.has(link.source) && nodeIds.has(link.target)
    );
    
    if (totalLinks > 0 && validLinks.length === 0 && process.env.NODE_ENV === 'development') {
      console.warn('⚠️ Alle Links wurden herausgefiltert!', {
        totalLinks,
        nodeCount: nodeIds.size,
        nodeIds: Array.from(nodeIds).slice(0, 10),
        sampleLink: displayLinks[0],
      });
    }
    
    // Finde verbundene Nodes für Focus Mode
    const connectedNodeIds = new Set<string>();
    if (hoveredNodeId) {
      connectedNodeIds.add(hoveredNodeId);
      displayLinks.forEach(link => {
        if (link.source === hoveredNodeId) connectedNodeIds.add(link.target);
        if (link.target === hoveredNodeId) connectedNodeIds.add(link.source);
      });
    }
    
    return validLinks
      .map((link, index) => {
        // Check if link is compromised (if either source or target is compromised)
        const sourceNode = reactFlowNodes.find(n => n.id === link.source);
        const targetNode = reactFlowNodes.find(n => n.id === link.target);
        const isCompromised = 
          (sourceNode?.data.status === 'compromised') ||
          (targetNode?.data.status === 'compromised');
        
        // Focus Mode: Dimme Edges die nicht zum hovered Node gehören
        const isConnectedToHovered = hoveredNodeId 
          ? (link.source === hoveredNodeId || link.target === hoveredNodeId)
          : true;

        return {
          id: `edge-${link.source}-${link.target}-${index}`,
          type: 'neural',
          source: link.source,
          target: link.target,
          data: {
            ...link,
            isCompromised,
            isDimmed: hoveredNodeId !== null && !isConnectedToHovered,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: isCompromised ? '#E53170' : getLinkColor(link.type, isCompromised),
          },
          animated: false, // Wir verwenden unsere eigenen Animationen
          style: {
            opacity: hoveredNodeId && !isConnectedToHovered ? 0.2 : 0.8,
            strokeWidth: isCompromised ? 3 : 2,
          },
        };
      });
  }, [displayLinks, reactFlowNodes, hoveredNodeId]);

  const [nodes, setNodes, onNodesChange] = useNodesState(reactFlowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(reactFlowEdges);

  // Update nodes and edges when data changes
  useEffect(() => {
    setNodes(reactFlowNodes.map(node => ({
      ...node,
      // Focus Mode: Dimme Nodes die nicht verbunden sind
      style: {
        opacity: hoveredNodeId 
          ? (node.id === hoveredNodeId ? 1 : 
             reactFlowEdges.some(e => 
               (e.source === hoveredNodeId && e.target === node.id) ||
               (e.target === hoveredNodeId && e.source === node.id)
             ) ? 0.8 : 0.2)
          : 1,
        transition: 'opacity 0.3s ease',
      },
    })));
  }, [reactFlowNodes, reactFlowEdges, hoveredNodeId, setNodes]);

  useEffect(() => {
    setEdges(reactFlowEdges);
  }, [reactFlowEdges, setEdges]);

  // Breathing Animation: Expand beim ersten Laden
  useEffect(() => {
    if (isInitialLayout && nodes.length > 0) {
      // Setze Initial Layout Flag nach kurzer Verzögerung zurück
      const timer = setTimeout(() => {
        setIsInitialLayout(false);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [isInitialLayout, nodes.length]);

  // Highlight selected node - Camera Fly-To Animation
  useEffect(() => {
    if (selectedInjectId && timelineEvents.length > 0) {
      const inject = timelineEvents.find((inj) => inj.inject_id === selectedInjectId);
      if (inject && inject.affected_assets.length > 0) {
        const nodeId = inject.affected_assets[0];
        setHighlightedNode(nodeId);
      }
    }
  }, [selectedInjectId, timelineEvents, setHighlightedNode]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setHighlightedNode(node.id);
  }, [setHighlightedNode]);

  const onNodeMouseEnter = useCallback((_event: React.MouseEvent, node: Node) => {
    setHoveredNodeId(node.id);
  }, []);

  const onNodeMouseLeave = useCallback(() => {
    setHoveredNodeId(null);
  }, []);

  const onPaneClick = useCallback(() => {
    setHighlightedNode(null);
    setHoveredNodeId(null);
  }, [setHighlightedNode]);

  const nodeTypesList = ['server', 'database', 'network', 'workstation'];
  const statusColors = [
    { status: 'online', color: '#2CB67D', label: 'Online' },
    { status: 'compromised', color: '#E53170', label: 'Compromised' },
    { status: 'degraded', color: '#D29922', label: 'Degraded' },
    { status: 'offline', color: '#8B949E', label: 'Offline' },
  ];

  const filteredNodesCount = reactFlowNodes.length;
  const filteredLinksCount = reactFlowEdges.length;

  return (
    <div className="flex h-full flex-col bg-[#090C10] min-h-0 relative">
      {/* Header - Layer 2: UI Overlay (z-index: 10) */}
      <div className="border-b border-[#30363D] p-4 flex-shrink-0 relative z-10 bg-[#161B22]/95 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-[#E6EDF3]">Digital Twin / Knowledge Graph</h2>
            <p className="text-sm text-[#8B949E]">
              {viewMode === 'god' 
                ? '👁️ God Mode: Ground Truth (Actual State) - Trainer-Sicht' 
                : '🛡️ Player Mode: Fog of War (Perceived State) - Manager-Sicht'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Scenario Loader */}
            <ScenarioLoader />
            
            {/* Filter Dropdown */}
            <Select
              value={filterType || 'all'}
              onValueChange={(value) => setFilterType(value === 'all' ? null : value)}
            >
              <SelectTrigger
                className="bg-[#161B22] border-[#30363D] text-[#E6EDF3] h-9 w-[140px]"
              >
                <SelectValue placeholder="Alle Typen" />
              </SelectTrigger>
              <SelectContent className="bg-[#161B22] border-[#30363D]">
                <SelectItem
                  value="all"
                  className="text-[#E6EDF3] hover:bg-[#30363D] focus:bg-[#30363D] cursor-pointer"
                >
                  Alle Typen
                </SelectItem>
                {nodeTypesList.map((type) => (
                  <SelectItem
                    key={type}
                    value={type}
                    className="text-[#E6EDF3] hover:bg-[#30363D] focus:bg-[#30363D] cursor-pointer"
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {/* UX View Mode Toggle: Player Mode vs God Mode */}
            <div className="flex items-center gap-1 rounded border border-[#30363D] bg-[#161B22] p-1">
              <button
                onClick={() => setViewMode('player')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === 'player'
                    ? 'bg-[#2CB67D] text-white'
                    : 'text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D]'
                }`}
                title="🛡️ Player Mode: Manager-Sicht (Fog of War - Perceived State)"
              >
                🛡️ Player
              </button>
              <button
                onClick={() => setViewMode('god')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === 'god'
                    ? 'bg-[#7F5AF0] text-white'
                    : 'text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D]'
                }`}
                title="👁️ God Mode: Trainer-Sicht (Ground Truth - Actual State)"
              >
                👁️ God
              </button>
            </div>
            
            {/* Mode Indicator */}
            <ModeIndicator />
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
              <span className="text-xs text-[#E6EDF3]">{filteredNodesCount} / {displayNodes.length}</span>
              <span className="text-xs text-[#8B949E]">•</span>
              <span className="text-xs text-[#E6EDF3]">{filteredLinksCount} / {displayLinks.length} Links</span>
              {displayLinks.length === 0 && (
                <span className="text-xs text-[#D29922]">⚠️ Keine Links gefunden</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* React Flow Canvas - Layer 1: Graph (Ganz unten, z-index: 1) */}
      {/* WICHTIG: Graph-Container hat KEINEN backdrop-filter - Nodes bleiben scharf */}
      <div className="relative flex-1 neural-graph-container" style={{ zIndex: 1, isolation: 'isolate' }}>
        {!graphReady ? (
          <div className="flex h-full items-center justify-center text-[#8B949E]">
            <div className="text-center">
              <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-[#7F5AF0] border-t-transparent mx-auto" />
              <p className="text-sm">Lade Digital Twin...</p>
            </div>
          </div>
        ) : displayNodes.length === 0 ? (
          <div className="flex h-full items-center justify-center text-[#8B949E]">
            <div className="text-center">
              <p className="text-sm">Keine Graph-Daten verfügbar</p>
              {DEMO_MODE && (
                <p className="mt-2 text-xs text-[#6E7681]">Demo-Mode: Prüfe DEMO_GRAPH_NODES</p>
              )}
            </div>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onNodeMouseEnter={onNodeMouseEnter}
            onNodeMouseLeave={onNodeMouseLeave}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            fitView={isInitialLayout}
            fitViewOptions={{ padding: 0.2, maxZoom: 1.5, duration: 1000 }}
            minZoom={0.1}
            maxZoom={4}
            defaultEdgeOptions={{
              type: 'neural',
            }}
            className={isInitialLayout ? 'breathing-animation' : ''}
          >
            {/* Layered Background: Semantische Schichten */}
            {/* WICHTIG: pointer-events-none damit Klicks durchgehen */}
            <Panel position="top-left" className="pointer-events-none" style={{ zIndex: 0 }}>
              <LayerBackground
                nodes={nodes}
                width={1200}
                height={800}
                affectedLayers={cascadingEffects.affectedLayers}
              />
            </Panel>
            
            {/* Grid-Hintergrund für technisches Mission Control Look */}
            <Background 
              gap={20} 
              size={1} 
              color="#1a1f2e" 
              variant="dots"
              style={{ backgroundColor: '#090C10' }}
            />
            
            {/* Mini-Map */}
            <MiniMap
              nodeColor={(node) => {
                const status = node.data?.status || 'online';
                switch (status) {
                  case 'compromised':
                    return '#E53170';
                  case 'degraded':
                    return '#D29922';
                  case 'offline':
                    return '#8B949E';
                default:
                    return '#2CB67D';
                }
              }}
              maskColor="rgba(9, 12, 16, 0.8)"
              style={{
                backgroundColor: '#161B22',
                border: '1px solid #30363D',
              }}
            />
            
            {/* Controls */}
            <Controls
              style={{
                backgroundColor: '#161B22',
                border: '1px solid #30363D',
              }}
              showInteractive={false}
            />
          </ReactFlow>
        )}
      </div>

      {/* Evaluation & Compliance Dashboard für Thesis - Layer 2: UI Overlay */}
      {showLegend && (
        <div className="border-t border-[#30363D] bg-[#161B22]/95 backdrop-blur-sm relative z-10 flex-shrink-0 flex flex-col" style={{ maxHeight: '40vh' }}>
          <div className="p-4 pb-2 flex-shrink-0">
            <h3 className="text-sm font-semibold text-[#E6EDF3]">Analysen & Evaluation</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 pt-2 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <EvaluationDashboard />
              <ComplianceScore />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <CoherenceChart />
              <ForensicTimeline />
            </div>
            <EvidenceMatrix />
          </div>
        </div>
      )}

      {/* Decision Point Modal (Interactive Mode) */}
      {interactiveMode && pendingDecision && (
        <DecisionPoint
          decisionId={pendingDecision.decision_id}
          question={pendingDecision.question}
          context={pendingDecision.context}
          options={pendingDecision.options}
          onDecision={(optionId) => {
            // TODO: Sende Entscheidung an Backend
            console.log('Decision made:', optionId);
            setPendingDecision(null);
          }}
        />
      )}

      {/* Footer mit Zeit-Slider - Layer 2: UI Overlay */}
      <div className="border-t border-[#30363D] p-4 relative z-10 bg-[#161B22]/95 backdrop-blur-sm">
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

      <style jsx global>{`
        .neural-graph-container {
          background: #090C10;
          background-image: 
            linear-gradient(rgba(127, 90, 240, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(127, 90, 240, 0.03) 1px, transparent 1px);
          background-size: 40px 40px;
        }

        .react-flow__node {
          background: transparent;
          transition: opacity 0.3s ease, transform 0.2s ease;
        }

        .react-flow__node:hover {
          z-index: 10;
        }

        .react-flow__handle {
          background: transparent;
          border: none;
        }
        
        /* Breathing Animation für Initial Layout */
        .breathing-animation .react-flow__node {
          animation: breathing 2s ease-in-out infinite;
        }

        @keyframes breathing {
          0%, 100% {
            transform: scale(1);
            opacity: 0.9;
          }
          50% {
            transform: scale(1.02);
            opacity: 1;
          }
        }

        .react-flow__controls {
          background: #161B22;
          border: 1px solid #30363D;
        }

        .react-flow__controls button {
          background: #161B22;
          border-bottom: 1px solid #30363D;
          color: #E6EDF3;
        }

        .react-flow__controls button:hover {
          background: #30363D;
        }

        .react-flow__minimap {
          background: #161B22;
          border: 1px solid #30363D;
        }

        .react-flow__background {
          background: #090C10;
        }
      `}</style>
    </div>
  );
}
