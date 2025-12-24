'use client';

import { useState, useEffect, useMemo } from 'react';
import { cruxAPI, type ScenarioListItem } from '@/lib/api';
import { useCruxStore } from '@/lib/store';

/**
 * Scenario Loader: Verbesserte Komponente zum Suchen und Laden gespeicherter Szenarien aus Neo4j
 */
export default function ScenarioLoader() {
  const { setInjects, setCurrentScenarioId, setCriticLogs } = useCruxStore();
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'injects' | 'type'>('date');

  useEffect(() => {
    if (isOpen && scenarios.length === 0) {
      loadScenarios();
    }
  }, [isOpen]);

  const loadScenarios = async () => {
    setLoading(true);
    setError(null);
    try {
      const loadedScenarios = await cruxAPI.listScenarios(100);
      setScenarios(loadedScenarios);
    } catch (err: any) {
      setError(err.message || 'Fehler beim Laden der Szenarien');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadScenario = async (scenarioId: string) => {
    setLoading(true);
    setError(null);
    try {
      const scenario = await cruxAPI.getScenario(scenarioId);
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/6266b006-7a5d-43a7-961c-cdfef45b541c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ScenarioLoader.tsx:40',message:'Received scenario from API',data:{scenario_id:scenarioId,injects_count:scenario.injects?.length,first_inject:scenario.injects?.[0] ? {inject_id:scenario.injects[0].inject_id,has_affected_assets:!!scenario.injects[0].affected_assets,affected_assets_type:typeof scenario.injects[0].affected_assets,affected_assets_value:scenario.injects[0].affected_assets} : null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      
      // Konvertiere Injects zu Store-Format
      const injects = scenario.injects.map((inj: any) => {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/6266b006-7a5d-43a7-961c-cdfef45b541c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ScenarioLoader.tsx:45',message:'Transforming inject',data:{inject_id:inj.inject_id,raw_affected_assets:inj.affected_assets,raw_affected_assets_type:typeof inj.affected_assets,transformed_affected_assets:inj.affected_assets || []},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
        // #endregion
        return {
          inject_id: inj.inject_id,
          time_offset: inj.time_offset,
          content: inj.content,
          phase: inj.phase,
          source: inj.source,
          target: inj.target,
          modality: inj.modality,
          technical_metadata: {
            mitre_id: inj.mitre_id || '',
            affected_assets: inj.affected_assets || [],
            severity: 'Medium' as const,
          },
          affected_assets: inj.affected_assets || [],
          dora_compliance_tag: inj.dora_compliance_tag,
          compliance_tags: inj.compliance_tags,
          created_at: new Date(),
        };
      });

      // Lade Critic Logs
      const logs = await cruxAPI.fetchScenarioLogs(scenarioId);

      // Setze State
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/6266b006-7a5d-43a7-961c-cdfef45b541c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ScenarioLoader.tsx:65',message:'Setting injects to store',data:{injects_count:injects.length,first_inject_has_affected_assets:!!injects[0]?.affected_assets,first_inject_affected_assets:injects[0]?.affected_assets},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      
      setInjects(injects);
      setCurrentScenarioId(scenarioId);
      setCriticLogs(logs);
      
      setIsOpen(false);
    } catch (err: any) {
      setError(err.message || 'Fehler beim Laden des Szenarios');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  // Filter und Sortierung
  const filteredAndSortedScenarios = useMemo(() => {
    let filtered = scenarios;

    // Suchfilter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.scenario_id.toLowerCase().includes(query) ||
          s.scenario_type?.toLowerCase().includes(query) ||
          s.current_phase?.toLowerCase().includes(query)
      );
    }

    // Typfilter
    if (filterType !== 'all') {
      filtered = filtered.filter((s) => s.scenario_type === filterType);
    }

    // Sortierung
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'date':
          const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
          const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
          return dateB - dateA; // Neueste zuerst
        case 'injects':
          return (b.inject_count || 0) - (a.inject_count || 0);
        case 'type':
          return (a.scenario_type || '').localeCompare(b.scenario_type || '');
        default:
          return 0;
      }
    });

    return filtered;
  }, [scenarios, searchQuery, filterType, sortBy]);

  // Eindeutige Typen für Filter
  const uniqueTypes = useMemo(() => {
    const types = new Set(scenarios.map((s) => s.scenario_type).filter(Boolean));
    return Array.from(types).sort();
  }, [scenarios]);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="rounded border border-[#30363D] bg-[#161B22] px-4 py-2 text-sm text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D] transition-colors flex items-center gap-2 font-medium"
      >
        <span>📂</span>
        <span>Gespeicherte Szenarien</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-4xl h-[85vh] rounded-lg border border-[#30363D] bg-[#0D1117] shadow-2xl flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-[#30363D] flex items-center justify-between bg-[#161B22]">
              <div>
                <h2 className="text-xl font-semibold text-[#E6EDF3] mb-1">
                  Gespeicherte Szenarien
                </h2>
                <p className="text-sm text-[#8B949E]">
                  {scenarios.length} Szenarien gefunden
                  {filteredAndSortedScenarios.length !== scenarios.length &&
                    ` • ${filteredAndSortedScenarios.length} gefiltert`}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={loadScenarios}
                  disabled={loading}
                  className="px-3 py-1.5 text-sm rounded border border-[#30363D] bg-[#161B22] text-[#7F5AF0] hover:bg-[#30363D] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  <span>🔄</span>
                  <span>Aktualisieren</span>
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-3 py-1.5 text-sm rounded border border-[#30363D] bg-[#161B22] text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D] transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Filter & Search Bar */}
            <div className="p-4 border-b border-[#30363D] bg-[#161B22] space-y-3">
              {/* Suchleiste */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Szenarien durchsuchen..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2.5 pl-10 rounded border border-[#30363D] bg-[#0D1117] text-[#E6EDF3] placeholder-[#8B949E] focus:outline-none focus:ring-2 focus:ring-[#7F5AF0] focus:border-transparent transition-all"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8B949E]">🔍</span>
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8B949E] hover:text-[#E6EDF3]"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* Filter & Sortierung */}
              <div className="flex items-center gap-3 flex-wrap">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-1.5 text-sm rounded border border-[#30363D] bg-[#0D1117] text-[#E6EDF3] focus:outline-none focus:ring-2 focus:ring-[#7F5AF0] focus:border-transparent"
                >
                  <option value="all">Alle Typen</option>
                  {uniqueTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </option>
                  ))}
                </select>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'date' | 'injects' | 'type')}
                  className="px-3 py-1.5 text-sm rounded border border-[#30363D] bg-[#0D1117] text-[#E6EDF3] focus:outline-none focus:ring-2 focus:ring-[#7F5AF0] focus:border-transparent"
                >
                  <option value="date">Sortiert nach Datum</option>
                  <option value="injects">Sortiert nach Injects</option>
                  <option value="type">Sortiert nach Typ</option>
                </select>
              </div>
            </div>

            {/* Content - Scrollbar */}
            <div className="flex-1 overflow-y-auto p-4 bg-[#0D1117]">
              {loading && scenarios.length === 0 ? (
                <div className="flex items-center justify-center py-16">
                  <div className="flex flex-col items-center gap-4">
                    <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#7F5AF0] border-t-transparent" />
                    <p className="text-sm text-[#8B949E]">Lade Szenarien...</p>
                  </div>
                </div>
              ) : error ? (
                <div className="p-4 rounded-lg bg-[#E53170]/10 border border-[#E53170] text-sm text-[#E53170]">
                  <div className="font-semibold mb-1">Fehler beim Laden</div>
                  <div>{error}</div>
                </div>
              ) : filteredAndSortedScenarios.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <div className="text-4xl mb-4">📭</div>
                  <p className="text-lg font-semibold text-[#E6EDF3] mb-2">
                    {searchQuery || filterType !== 'all'
                      ? 'Keine Szenarien gefunden'
                      : 'Keine gespeicherten Szenarien'}
                  </p>
                  <p className="text-sm text-[#8B949E]">
                    {searchQuery || filterType !== 'all'
                      ? 'Versuche andere Suchbegriffe oder Filter'
                      : 'Generiere ein neues Szenario, um es hier zu sehen'}
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredAndSortedScenarios.map((scenario) => (
                    <div
                      key={scenario.scenario_id}
                      className="rounded-lg border border-[#30363D] bg-[#161B22] p-4 hover:border-[#7F5AF0]/50 hover:bg-[#1C2128] transition-all cursor-pointer group"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-mono font-semibold text-[#7F5AF0] mb-2 truncate">
                            {scenario.scenario_id}
                          </div>
                          <div className="space-y-1.5">
                            <div className="flex items-center gap-2 text-xs text-[#8B949E]">
                              <span className="font-semibold text-[#E6EDF3]">Typ:</span>
                              <span className="px-2 py-0.5 rounded bg-[#30363D] text-[#E6EDF3]">
                                {scenario.scenario_type?.replace(/_/g, ' ') || 'N/A'}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-[#8B949E]">
                              <span className="font-semibold text-[#E6EDF3]">Phase:</span>
                              <span>{scenario.current_phase || 'N/A'}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-[#8B949E]">
                              <span className="font-semibold text-[#E6EDF3]">Injects:</span>
                              <span className="px-2 py-0.5 rounded bg-[#2CB67D]/20 text-[#2CB67D]">
                                {scenario.inject_count || 0}
                              </span>
                            </div>
                            {scenario.created_at && (
                              <div className="flex items-center gap-2 text-xs text-[#8B949E]">
                                <span className="font-semibold text-[#E6EDF3]">Erstellt:</span>
                                <span>{formatDate(scenario.created_at)}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleLoadScenario(scenario.scenario_id)}
                        disabled={loading}
                        className="w-full mt-3 px-4 py-2 text-sm rounded-lg bg-[#7F5AF0] text-white hover:bg-[#6D4DD4] disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium group-hover:bg-[#6D4DD4]"
                      >
                        {loading ? (
                          <span className="flex items-center justify-center gap-2">
                            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                            <span>Lädt...</span>
                          </span>
                        ) : (
                          'Szenario öffnen'
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
