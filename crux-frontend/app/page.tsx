'use client';

import ScenarioComposer from '@/components/ScenarioComposer';
import DigitalTwinGraph from '@/components/DigitalTwinGraph';
import ForensicTrace from '@/components/ForensicTrace';
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
        console.log('Loading data from backend...');
        
        // Lade Graph-Daten
        const [nodes, links] = await Promise.all([
          cruxAPI.fetchGraphNodes(),
          cruxAPI.fetchGraphLinks(),
        ]);
        
        if (nodes.length > 0 || links.length > 0) {
          setGraphData(nodes, links);
          setBackendConnected(true);
          console.log(`Loaded ${nodes.length} nodes and ${links.length} links`);
        }

        // Lade neuestes Szenario
        const scenarioData = await cruxAPI.fetchLatestScenario();
        if (scenarioData.scenario_id && scenarioData.injects.length > 0) {
          setCurrentScenarioId(scenarioData.scenario_id);
          setInjects(scenarioData.injects);
          console.log(`Loaded scenario ${scenarioData.scenario_id} with ${scenarioData.injects.length} injects`);

          // Lade Logs für das Szenario
          const logs = await cruxAPI.fetchScenarioLogs(scenarioData.scenario_id);
          if (logs.length > 0) {
            setCriticLogs(logs);
            console.log(`Loaded ${logs.length} critic logs`);
          }
        }
      } catch (error) {
        console.error('Error loading backend data:', error);
        setBackendConnected(false);
        // Fallback zu Demo-Daten wenn Backend nicht verfügbar
        setGraphData(DEMO_GRAPH_NODES, DEMO_GRAPH_LINKS);
        setCriticLogs(DEMO_CRITIC_LOGS);
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
              <div className="text-right">
                <div className="text-xs text-[#8B949E]">Backend</div>
                <div className={`text-sm font-semibold ${backendConnected ? 'text-symbolic' : 'text-warning'}`}>
                  {backendConnected ? '✓ Verbunden' : '✗ Offline'}
                </div>
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

      {/* Main 3-Column Layout */}
      <main className="flex flex-1 overflow-hidden">
        {/* Panel A: Scenario Composer (30%) */}
        <div className="w-[30%] border-r border-[#30363D]">
          <ScenarioComposer />
        </div>

        {/* Panel B: Digital Twin Graph (50%) */}
        <div className="w-[50%] border-r border-[#30363D]">
          <DigitalTwinGraph />
        </div>

        {/* Panel C: Forensic Trace (20%) */}
        <div className="w-[20%]">
          <ForensicTrace />
        </div>
      </main>
    </div>
  );
}
