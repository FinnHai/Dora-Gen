'use client';

import { useMemo } from 'react';
import { useCruxStore } from '@/lib/store';

/**
 * Compliance Score: DORA & NIS2 Compliance Visualisierung
 * 
 * Zeigt wie gut ein Szenario die regulatorischen Anforderungen erfüllt.
 * Dies zeigt die wirtschaftliche Relevanz des Tools.
 */
export default function ComplianceScore() {
  const { injects, criticLogs } = useCruxStore();

  const complianceMetrics = useMemo(() => {
    // DORA Requirements (vereinfacht)
    const doraRequirements = [
      { id: 'bc', label: 'Business Continuity', covered: false },
      { id: 'recovery', label: 'Recovery Testing', covered: false },
      { id: 'incident', label: 'Incident Response', covered: false },
      { id: 'monitoring', label: 'Monitoring & Detection', covered: false },
      { id: 'communication', label: 'Crisis Communication', covered: false },
    ];

    // Prüfe welche Requirements durch Injects abgedeckt werden
    injects.forEach(inject => {
      const contentLower = inject.content.toLowerCase();
      const phaseLower = inject.phase?.toLowerCase() || '';

      if (contentLower.includes('continuity') || contentLower.includes('backup')) {
        doraRequirements[0].covered = true;
      }
      if (contentLower.includes('recovery') || contentLower.includes('restore')) {
        doraRequirements[1].covered = true;
      }
      if (phaseLower.includes('incident') || contentLower.includes('response')) {
        doraRequirements[2].covered = true;
      }
      if (contentLower.includes('detect') || contentLower.includes('alert') || contentLower.includes('monitor')) {
        doraRequirements[3].covered = true;
      }
      if (contentLower.includes('communicat') || contentLower.includes('notify')) {
        doraRequirements[4].covered = true;
      }
    });

    const coveredCount = doraRequirements.filter(r => r.covered).length;
    const coverageScore = (coveredCount / doraRequirements.length) * 100;

    return {
      requirements: doraRequirements,
      coveredCount,
      totalCount: doraRequirements.length,
      coverageScore,
    };
  }, [injects]);

  return (
    <div className="rounded border border-[#30363D] bg-[#161B22] p-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[#E6EDF3] mb-1">
          DORA Compliance Score
        </h3>
        <p className="text-xs text-[#8B949E]">
          Regulatorische Anforderungen Abdeckung
        </p>
      </div>

      {/* Coverage Score */}
      <div className="mb-4 p-3 rounded border border-[#30363D] bg-[#090C10]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-[#8B949E]">Coverage</span>
          <span className="text-2xl font-bold font-data text-[#2CB67D]">
            {complianceMetrics.coverageScore.toFixed(0)}%
          </span>
        </div>
        <div className="text-xs text-[#8B949E] mb-2">
          {complianceMetrics.coveredCount} von {complianceMetrics.totalCount} Requirements abgedeckt
        </div>
        <div className="h-2 bg-[#30363D] rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[#2CB67D] to-[#7F5AF0] transition-all duration-500"
            style={{ width: `${complianceMetrics.coverageScore}%` }}
          />
        </div>
      </div>

      {/* Requirements Checklist */}
      <div className="space-y-2">
        {complianceMetrics.requirements.map((req) => (
          <div
            key={req.id}
            className="flex items-center gap-2 text-xs"
          >
            <div
              className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                req.covered
                  ? 'bg-[#2CB67D] border-[#2CB67D]'
                  : 'bg-transparent border-[#30363D]'
              }`}
            >
              {req.covered && (
                <svg className="w-3 h-3 text-[#090C10]" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <span className={req.covered ? 'text-[#E6EDF3]' : 'text-[#8B949E]'}>
              {req.label}
            </span>
          </div>
        ))}
      </div>

      {/* Thesis Value Note */}
      <div className="mt-4 pt-4 border-t border-[#30363D]">
        <p className="text-xs text-[#8B949E] italic">
          💼 <strong className="text-[#E6EDF3]">Wirtschaftliche Relevanz:</strong> Unternehmen müssen gesetzlich Krisenszenarien testen (DORA, NIS2).
          CRUX automatisiert diese Compliance-Validierung.
        </p>
      </div>
    </div>
  );
}

