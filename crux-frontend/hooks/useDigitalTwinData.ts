/**
 * Digital Twin Data Hook: Verwaltet Topology und Timeline Events
 * 
 * Diese Hook ist die "Hydra State" - sie verwaltet zwei Datenströme:
 * 1. Stream A (Live Graph): Topology aus Neo4j
 * 2. Stream B (Forensic Timeline): Events aus LangGraph State / Forensic Logs
 */

import { useState, useEffect, useCallback } from 'react';
import { cruxAPI, GraphNode, GraphLink, Inject, CriticLog } from '@/lib/api';
import { transformNeo4jToGraph, BackendNode, BackendLink } from '@/lib/graphTransformer';
import { useCruxStore } from '@/lib/store';

export type DataMode = 'LIVE' | 'FORENSIC' | 'DEMO';

interface UseDigitalTwinDataReturn {
  graphNodes: GraphNode[];
  graphLinks: GraphLink[];
  timelineEvents: Inject[];
  criticLogs: CriticLog[];
  mode: DataMode;
  isLoading: boolean;
  error: string | null;
  handleFileUpload: (file: File) => Promise<void>;
  setMode: (mode: DataMode) => void;
  refreshTopology: () => Promise<void>;
  refreshTimeline: () => Promise<void>;
}

/**
 * Verarbeitet Logs für Timeline-Darstellung
 */
function processLogsForTimeline(logs: CriticLog[]): Inject[] {
  // Extrahiere Injects aus CriticLogs
  // (Dies hängt von der genauen Struktur der Logs ab)
  const injects: Inject[] = [];
  
  logs.forEach(log => {
    if (log.inject_id && log.details?.validation) {
      // Versuche Inject aus Log zu rekonstruieren
      // (Dies ist ein vereinfachtes Beispiel - sollte an echte Datenstruktur angepasst werden)
      const inject: Inject = {
        inject_id: log.inject_id,
        time_offset: log.timestamp, // Oder aus anderen Feldern
        content: log.message,
        status: log.details.validation.is_valid ? 'verified' : 'rejected',
        phase: 'UNKNOWN',
        source: 'Unknown',
        target: 'Unknown',
        modality: 'SIEM Alert',
        affected_assets: [], // Sollte aus Log extrahiert werden
      };
      injects.push(inject);
    }
  });
  
  return injects;
}

/**
 * Haupt-Hook für Digital Twin Datenverwaltung
 */
export function useDigitalTwinData(scenarioId: string | null): UseDigitalTwinDataReturn {
  const [mode, setMode] = useState<DataMode>('DEMO');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    graphNodes,
    graphLinks,
    injects,
    criticLogs,
    setGraphData,
    setInjects,
    setCriticLogs,
    setCurrentScenarioId,
  } = useCruxStore();

  // 1. Lade Ground Truth (Topology) aus Neo4j
  const fetchTopology = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [backendNodes, backendLinks] = await Promise.all([
        cruxAPI.fetchGraphNodes(),
        cruxAPI.fetchGraphLinks(),
      ]);

      // Transformiere Backend-Daten zu Frontend-Format
      const transformed = transformNeo4jToGraph(
        backendNodes as BackendNode[],
        backendLinks as BackendLink[],
        { initialScatter: true }
      );

      setGraphData(transformed.nodes, transformed.links);
    } catch (err) {
      console.error('Error fetching topology:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch topology');
    } finally {
      setIsLoading(false);
    }
  }, [setGraphData]);

  // 2. Lade Timeline Events
  const fetchTimeline = useCallback(async () => {
    if (!scenarioId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Option A: Lade aus Scenario Logs
      const logs = await cruxAPI.fetchScenarioLogs(scenarioId);
      setCriticLogs(logs);
      
      // Option B: Lade Injects direkt (falls verfügbar)
      const scenarioData = await cruxAPI.fetchLatestScenario();
      if (scenarioData.injects) {
        setInjects(scenarioData.injects);
      }
    } catch (err) {
      console.error('Error fetching timeline:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch timeline');
    } finally {
      setIsLoading(false);
    }
  }, [scenarioId, setInjects, setCriticLogs]);

  // 3. Poll für Updates (Live Mode)
  useEffect(() => {
    if (mode === 'LIVE' && scenarioId) {
      const interval = setInterval(() => {
        fetchTimeline();
      }, 2000); // Poll alle 2 Sekunden
      
      return () => clearInterval(interval);
    }
  }, [mode, scenarioId, fetchTimeline]);

  // 4. Initial Load
  useEffect(() => {
    if (mode !== 'DEMO') {
      fetchTopology();
      if (scenarioId) {
        fetchTimeline();
      }
    }
  }, [mode, scenarioId, fetchTopology, fetchTimeline]);

  // 5. Handle File Upload (Forensic Mode)
  const handleFileUpload = useCallback(async (file: File) => {
    setIsLoading(true);
    setError(null);
    setMode('FORENSIC');
    
    try {
      const result = await cruxAPI.uploadForensicTrace(file);
      
      // Setze Logs
      setCriticLogs(result.logs);
      
      // Optionally: Refresh topology wenn Log-Datei Architektur-Daten enthält
      // fetchTopology();
      
      console.log(`✅ Forensic trace uploaded: ${result.logs_count} logs`);
    } catch (err) {
      console.error('Error uploading forensic trace:', err);
      setError(err instanceof Error ? err.message : 'Failed to upload forensic trace');
    } finally {
      setIsLoading(false);
    }
  }, [setCriticLogs]);

  // 6. Refresh Functions
  const refreshTopology = useCallback(async () => {
    await fetchTopology();
  }, [fetchTopology]);

  const refreshTimeline = useCallback(async () => {
    await fetchTimeline();
  }, [fetchTimeline]);

  return {
    graphNodes,
    graphLinks,
    timelineEvents: injects,
    criticLogs,
    mode,
    isLoading,
    error,
    handleFileUpload,
    setMode,
    refreshTopology,
    refreshTimeline,
  };
}

