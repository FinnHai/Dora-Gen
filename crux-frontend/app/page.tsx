'use client';

import ScenarioComposer from '@/components/ScenarioComposer';
import DigitalTwinGraph from '@/components/DigitalTwinGraph';
import ForensicTrace from '@/components/ForensicTrace';
import CriticValidationPanel from '@/components/CriticValidationPanel';
import WorkflowVisualization from '@/components/WorkflowVisualization';
import ScenarioGenerator from '@/components/ScenarioGenerator';
import { ResizablePanel } from '@/components/ResizablePanel';
import { useCruxStore } from '@/lib/store';
import { useEffect, useState } from 'react';
import { DEMO_MODE, DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS, DEMO_CRITIC_LOGS, DEMO_INJECTS, playDemoFlow, REAL_SCENARIO_ID } from '@/lib/demo-data';
import { cruxAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';

export default function Home() {
  const { 
    setGraphData, 
    setCriticLogs,
    setInjects,
    addInject, 
    updateInject, 
    addCriticLog, 
    setHighlightedNode,
    clearInjects,
    clearLogs
  } = useCruxStore();
  const [demoPlaying, setDemoPlaying] = useState(false);
  const [loading, setLoading] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);
  const [currentScenarioId, setCurrentScenarioId] = useState<string | null>(null);
  const [showTransparencyMode, setShowTransparencyMode] = useState(false);
  
  // Panel-Größen für Transparency Mode
  const [transparencyWidths, setTransparencyWidths] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('crux-transparency-widths');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (parsed.a && parsed.b && parsed.c && parsed.d) {
            return parsed;
          }
        } catch {}
      }
    }
    return { a: 25, b: 35, c: 20, d: 20 };
  });
  
  // Panel-Größen für Normal Mode
  const [normalWidths, setNormalWidths] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('crux-normal-widths');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (parsed.a && parsed.b && parsed.c) {
            return parsed;
          }
        } catch {}
      }
    }
    return { a: 30, b: 50, c: 20 };
  });

  // Lade Daten vom Backend oder Demo-Mode
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      
      if (DEMO_MODE) {
        // Demo-Mode: Verwende echte Daten aus Forensic Logs
        setGraphData(DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS);
        setCriticLogs(DEMO_CRITIC_LOGS);
        setInjects(DEMO_INJECTS);
        setCurrentScenarioId(REAL_SCENARIO_ID);
        setBackendConnected(false);
        setLoading(false);
        return;
      }

      try {
        // Backend-Mode: Lade echte Daten
        console.log('🔄 Loading data from backend...');
        
        // Lade Graph-Daten (immer zuerst, auch wenn leer)
        const [nodes, links] = await Promise.all([
          cruxAPI.fetchGraphNodes(),
          cruxAPI.fetchGraphLinks(),
        ]);
        
        console.log(`📊 Graph: ${nodes.length} nodes, ${links.length} links`);
        
        if (nodes.length > 0 || links.length > 0) {
          setGraphData(nodes, links);
          setBackendConnected(true);
        } else {
          // Auch wenn leer, Backend ist verbunden
          setBackendConnected(true);
          console.log('⚠️ No graph data yet - backend connected but empty');
        }

        // Lade neuestes Szenario
        const scenarioData = await cruxAPI.fetchLatestScenario();
        console.log(`📋 Scenario: ${scenarioData.scenario_id || 'None'}, ${scenarioData.injects.length} injects`);
        
        if (scenarioData.scenario_id) {
          setCurrentScenarioId(scenarioData.scenario_id);
          
          if (scenarioData.injects.length > 0) {
            setInjects(scenarioData.injects);
            console.log(`✅ Loaded scenario ${scenarioData.scenario_id} with ${scenarioData.injects.length} injects`);

            // Lade Logs für das Szenario
            const logs = await cruxAPI.fetchScenarioLogs(scenarioData.scenario_id);
            if (logs.length > 0) {
              setCriticLogs(logs);
              console.log(`📝 Loaded ${logs.length} critic logs`);
            }
          } else {
            console.log('⚠️ Scenario exists but no injects yet');
            setInjects([]);
          }
        } else {
          console.log('⚠️ No scenario found - backend may be empty');
          setInjects([]);
        }
      } catch (error) {
        console.error('❌ Error loading backend data:', error);
        setBackendConnected(false);
        // Fallback zu Demo-Daten wenn Backend nicht verfügbar
        console.log('🔄 Falling back to demo data...');
        setGraphData(DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS);
        setCriticLogs(DEMO_CRITIC_LOGS);
        setInjects(DEMO_INJECTS);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [setGraphData, setCriticLogs, setInjects]);

  // Demo-Flow Handler
  const handlePlayDemo = async () => {
    if (demoPlaying) return;
    
    setDemoPlaying(true);
    
    // Reset für saubere Demo
    clearInjects();
    clearLogs();
    setHighlightedNode(null);
    
    // Kurze Pause für Reset-Animation
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Delay-Funktion für Animationen
    const delay = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms));
    
    try {
      await playDemoFlow(
        addInject,
        updateInject,
        addCriticLog,
        setHighlightedNode,
        delay
      );
    } finally {
      setDemoPlaying(false);
    }
  };

  return (
    <div className="flex h-screen flex-col bg-[#090C10]">
      {/* Header */}
      <header className="border-b border-[#30363D] bg-[#161B22] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#E6EDF3]">CRUX</h1>
            <p className="text-sm text-[#8B949E]">
              The Glass Box - Neuro-Symbolic Crisis Scenario Generator
            </p>
          </div>
          <div className="flex items-center gap-4">
            {!DEMO_MODE && (
              <ScenarioGenerator
                onGenerate={(scenarioId, injects) => {
                  console.log(`Scenario ${scenarioId} generated with ${injects.length} injects`);
                }}
              />
            )}
            <Button
              onClick={() => setShowTransparencyMode(!showTransparencyMode)}
              className="bg-symbolic hover:bg-symbolic/80 text-white font-semibold px-4 py-2 rounded-md transition-all text-sm"
            >
              {showTransparencyMode ? 'Hide' : 'Show'} Transparency
            </Button>
            {DEMO_MODE && (
              <Button
                onClick={handlePlayDemo}
                disabled={demoPlaying}
                className="bg-[#7F5AF0] hover:bg-[#7F5AF0]/80 text-white font-semibold px-6 py-2 rounded-md transition-all"
              >
                {demoPlaying ? (
                  <>
                    <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Demo läuft...
                  </>
                ) : (
                  <>
                    <span className="mr-2">▶</span>
                    Play Demo
                  </>
                )}
              </Button>
            )}
            {loading && (
              <div className="flex items-center gap-2 text-[#8B949E]">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#7F5AF0] border-t-transparent" />
                <span className="text-sm">Lade Daten...</span>
              </div>
            )}
            {!loading && (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs text-[#8B949E]">Backend</div>
                  <div className={`text-sm font-semibold ${backendConnected ? 'text-symbolic' : 'text-intervention'}`}>
                    {backendConnected ? 'Verbunden' : 'Offline'}
                  </div>
                </div>
                {!DEMO_MODE && (
                  <button
                    onClick={async () => {
                      setLoading(true);
                      try {
                        console.log('Refreshing data...');
                        const [nodes, links] = await Promise.all([
                          cruxAPI.fetchGraphNodes(),
                          cruxAPI.fetchGraphLinks(),
                        ]);
                        if (nodes.length > 0 || links.length > 0) {
                          setGraphData(nodes, links);
                        }
                        const scenarioData = await cruxAPI.fetchLatestScenario();
                        if (scenarioData.scenario_id) {
                          setCurrentScenarioId(scenarioData.scenario_id);
                          setInjects(scenarioData.injects);
                          const logs = await cruxAPI.fetchScenarioLogs(scenarioData.scenario_id);
                          if (logs.length > 0) {
                            setCriticLogs(logs);
                          }
                        }
                        setBackendConnected(true);
                        console.log('Refresh complete');
                      } catch (error) {
                        console.error('Refresh error:', error);
                        setBackendConnected(false);
                      } finally {
                        setLoading(false);
                      }
                    }}
                    className="px-3 py-1.5 bg-[#161B22] hover:bg-[#30363D] text-[#8B949E] hover:text-[#E6EDF3] text-sm rounded-md transition-all border border-[#30363D]"
                    disabled={loading}
                  >
                    Refresh
                  </button>
                )}
              </div>
            )}
            {currentScenarioId && (
              <div className="text-right">
                <div className="text-xs text-[#8B949E]">Szenario</div>
                <div className="text-sm font-semibold text-[#E6EDF3] font-data">{currentScenarioId}</div>
              </div>
            )}
            <div className="text-right">
              <div className="text-xs text-[#8B949E]">Reality Score</div>
              <div className="text-lg font-semibold text-symbolic">98%</div>
            </div>
            {DEMO_MODE && (
              <div className="text-right">
                <div className="text-xs text-[#8B949E]">Mode</div>
                <div className="text-sm font-semibold text-[#7F5AF0]">DEMO</div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="flex flex-1 overflow-hidden min-h-0">
        {showTransparencyMode ? (
          /* Transparency Mode: 4-Column Layout */
          <>
            {/* Panel A: Scenario Composer */}
            <ResizablePanel
              defaultWidth={transparencyWidths.a}
              minWidth={15}
              maxWidth={50}
              onResize={(w) => {
                const diff = w - transparencyWidths.a;
                const otherTotal = transparencyWidths.b + transparencyWidths.c + transparencyWidths.d;
                const newWidths = {
                  a: w,
                  b: transparencyWidths.b,
                  c: transparencyWidths.c,
                  d: transparencyWidths.d
                };
                // Verteile die Differenz proportional auf die anderen Panels
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.b = Math.max(15, transparencyWidths.b * scale);
                  newWidths.c = Math.max(15, transparencyWidths.c * scale);
                  newWidths.d = Math.max(15, transparencyWidths.d * scale);
                }
                // Stelle sicher, dass die Summe genau 100% ist
                const sum = newWidths.a + newWidths.b + newWidths.c + newWidths.d;
                const correction = 100 - sum;
                newWidths.d += correction;
                setTransparencyWidths(newWidths);
                localStorage.setItem('crux-transparency-widths', JSON.stringify(newWidths));
              }}
              className="border-r border-[#30363D] overflow-y-auto"
            >
              <ScenarioComposer />
            </ResizablePanel>

            {/* Panel B: Digital Twin Graph */}
            <ResizablePanel
              defaultWidth={transparencyWidths.b}
              minWidth={20}
              maxWidth={60}
              onResize={(w) => {
                const diff = w - transparencyWidths.b;
                const otherTotal = transparencyWidths.a + transparencyWidths.c + transparencyWidths.d;
                const newWidths = {
                  a: transparencyWidths.a,
                  b: w,
                  c: transparencyWidths.c,
                  d: transparencyWidths.d
                };
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.a = Math.max(15, transparencyWidths.a * scale);
                  newWidths.c = Math.max(15, transparencyWidths.c * scale);
                  newWidths.d = Math.max(15, transparencyWidths.d * scale);
                }
                const sum = newWidths.a + newWidths.b + newWidths.c + newWidths.d;
                const correction = 100 - sum;
                newWidths.d += correction;
                setTransparencyWidths(newWidths);
                localStorage.setItem('crux-transparency-widths', JSON.stringify(newWidths));
              }}
              className="border-r border-[#30363D]"
            >
              <DigitalTwinGraph />
            </ResizablePanel>

            {/* Panel C: Critic Validation */}
            <ResizablePanel
              defaultWidth={transparencyWidths.c}
              minWidth={15}
              maxWidth={40}
              onResize={(w) => {
                const diff = w - transparencyWidths.c;
                const otherTotal = transparencyWidths.a + transparencyWidths.b + transparencyWidths.d;
                const newWidths = {
                  a: transparencyWidths.a,
                  b: transparencyWidths.b,
                  c: w,
                  d: transparencyWidths.d
                };
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.a = Math.max(15, transparencyWidths.a * scale);
                  newWidths.b = Math.max(20, transparencyWidths.b * scale);
                  newWidths.d = Math.max(15, transparencyWidths.d * scale);
                }
                const sum = newWidths.a + newWidths.b + newWidths.c + newWidths.d;
                const correction = 100 - sum;
                newWidths.d += correction;
                setTransparencyWidths(newWidths);
                localStorage.setItem('crux-transparency-widths', JSON.stringify(newWidths));
              }}
              className="border-r border-[#30363D] overflow-y-auto"
            >
              <div className="h-full p-4">
                <CriticValidationPanel />
              </div>
            </ResizablePanel>

            {/* Panel D: Workflow & Forensic Trace */}
            <ResizablePanel
              defaultWidth={transparencyWidths.d}
              minWidth={15}
              maxWidth={40}
              onResize={(w) => {
                const diff = w - transparencyWidths.d;
                const otherTotal = transparencyWidths.a + transparencyWidths.b + transparencyWidths.c;
                const newWidths = {
                  a: transparencyWidths.a,
                  b: transparencyWidths.b,
                  c: transparencyWidths.c,
                  d: w
                };
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.a = Math.max(15, transparencyWidths.a * scale);
                  newWidths.b = Math.max(20, transparencyWidths.b * scale);
                  newWidths.c = Math.max(15, transparencyWidths.c * scale);
                }
                const sum = newWidths.a + newWidths.b + newWidths.c + newWidths.d;
                const correction = 100 - sum;
                newWidths.c += correction;
                setTransparencyWidths(newWidths);
                localStorage.setItem('crux-transparency-widths', JSON.stringify(newWidths));
              }}
              className="overflow-y-auto"
            >
              <div className="h-full p-4 space-y-4">
                <WorkflowVisualization />
                <div className="mt-4">
                  <ForensicTrace />
                </div>
              </div>
            </ResizablePanel>
          </>
        ) : (
          /* Normal Mode: 3-Column Layout */
          <>
            {/* Panel A: Scenario Composer */}
            <ResizablePanel
              defaultWidth={normalWidths.a}
              minWidth={15}
              maxWidth={50}
              onResize={(w) => {
                const diff = w - normalWidths.a;
                const otherTotal = normalWidths.b + normalWidths.c;
                const newWidths = {
                  a: w,
                  b: normalWidths.b,
                  c: normalWidths.c
                };
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.b = Math.max(30, normalWidths.b * scale);
                  newWidths.c = Math.max(15, normalWidths.c * scale);
                }
                const sum = newWidths.a + newWidths.b + newWidths.c;
                const correction = 100 - sum;
                newWidths.c += correction;
                setNormalWidths(newWidths);
                localStorage.setItem('crux-normal-widths', JSON.stringify(newWidths));
              }}
              className="border-r border-[#30363D] overflow-y-auto"
            >
              <ScenarioComposer />
            </ResizablePanel>

            {/* Panel B: Digital Twin Graph */}
            <ResizablePanel
              defaultWidth={normalWidths.b}
              minWidth={30}
              maxWidth={70}
              onResize={(w) => {
                const diff = w - normalWidths.b;
                const otherTotal = normalWidths.a + normalWidths.c;
                const newWidths = {
                  a: normalWidths.a,
                  b: w,
                  c: normalWidths.c
                };
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.a = Math.max(15, normalWidths.a * scale);
                  newWidths.c = Math.max(15, normalWidths.c * scale);
                }
                const sum = newWidths.a + newWidths.b + newWidths.c;
                const correction = 100 - sum;
                newWidths.c += correction;
                setNormalWidths(newWidths);
                localStorage.setItem('crux-normal-widths', JSON.stringify(newWidths));
              }}
              className="border-r border-[#30363D]"
            >
              <DigitalTwinGraph />
            </ResizablePanel>

            {/* Panel C: Forensic Trace */}
            <ResizablePanel
              defaultWidth={normalWidths.c}
              minWidth={15}
              maxWidth={40}
              onResize={(w) => {
                const diff = w - normalWidths.c;
                const otherTotal = normalWidths.a + normalWidths.b;
                const newWidths = {
                  a: normalWidths.a,
                  b: normalWidths.b,
                  c: w
                };
                if (otherTotal > 0) {
                  const scale = (otherTotal - diff) / otherTotal;
                  newWidths.a = Math.max(15, normalWidths.a * scale);
                  newWidths.b = Math.max(30, normalWidths.b * scale);
                }
                const sum = newWidths.a + newWidths.b + newWidths.c;
                const correction = 100 - sum;
                newWidths.b += correction;
                setNormalWidths(newWidths);
                localStorage.setItem('crux-normal-widths', JSON.stringify(newWidths));
              }}
              className="overflow-y-auto"
            >
              <ForensicTrace />
            </ResizablePanel>
          </>
        )}
      </main>
    </div>
  );
}
