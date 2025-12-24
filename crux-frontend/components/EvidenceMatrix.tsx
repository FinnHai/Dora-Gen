'use client';

import { useState, useMemo } from 'react';
import { useCruxStore } from '@/lib/store';
import { runAllTests, type TestResult } from '@/lib/qa-framework';

/**
 * Evidence Matrix: Quality Assurance Dashboard für Thesis-Beweisführung
 * 
 * Zeigt die Ergebnisse der 4 strategischen Testszenarien:
 * 1. Kausalitäts-Stresstest
 * 2. Amnesie-Test
 * 3. DORA-Compliance Audit
 * 4. Kettenreaktion-Test
 */
export default function EvidenceMatrix() {
  const { injects, criticLogs, graphNodes, graphLinks } = useCruxStore();
  const [expandedTest, setExpandedTest] = useState<string | null>(null);

  const evidenceMatrix = useMemo(() => {
    if (injects.length === 0) {
      return null;
    }
    return runAllTests(injects, criticLogs, graphNodes, graphLinks);
  }, [injects, criticLogs, graphNodes, graphLinks]);

  if (!evidenceMatrix) {
    return (
      <div className="rounded border border-[#30363D] bg-[#161B22] p-4">
        <h3 className="text-sm font-semibold text-[#E6EDF3] mb-2">
          Evidence Matrix
        </h3>
        <p className="text-xs text-[#8B949E]">
          Keine Test-Daten verfügbar. Generiere ein Szenario um Tests durchzuführen.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded border border-[#30363D] bg-[#161B22] p-4">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-[#E6EDF3]">
            Evidence Matrix - Quality Assurance Framework
          </h3>
          <div className="flex items-center gap-2">
            <span className={`text-xs font-bold ${
              evidenceMatrix.overallScore >= 75 ? 'text-[#2CB67D]' :
              evidenceMatrix.overallScore >= 50 ? 'text-[#D29922]' :
              'text-[#E53170]'
            }`}>
              {evidenceMatrix.overallScore.toFixed(0)}%
            </span>
            <span className="text-xs text-[#8B949E]">
              ({evidenceMatrix.passedTests}/{evidenceMatrix.totalTests} Tests bestanden)
            </span>
          </div>
        </div>
        <p className="text-xs text-[#8B949E]">
          Strategische Testszenarien zur Beweisführung der Neuro-Symbolischen Architektur
        </p>
      </div>

      {/* Overall Score */}
      <div className="mb-4 p-3 rounded border border-[#30363D] bg-[#090C10]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-[#8B949E]">Overall Score</span>
          <span className={`text-2xl font-bold font-data ${
            evidenceMatrix.overallScore >= 75 ? 'text-[#2CB67D]' :
            evidenceMatrix.overallScore >= 50 ? 'text-[#D29922]' :
            'text-[#E53170]'
          }`}>
            {evidenceMatrix.overallScore.toFixed(1)}%
          </span>
        </div>
        <div className="h-2 bg-[#30363D] rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              evidenceMatrix.overallScore >= 75 ? 'bg-[#2CB67D]' :
              evidenceMatrix.overallScore >= 50 ? 'bg-[#D29922]' :
              'bg-[#E53170]'
            }`}
            style={{ width: `${evidenceMatrix.overallScore}%` }}
          />
        </div>
      </div>

      {/* Test Results Table */}
      <div className="space-y-2">
        {evidenceMatrix.testResults.map((test) => (
          <TestResultCard
            key={test.testId}
            test={test}
            isExpanded={expandedTest === test.testId}
            onToggle={() => setExpandedTest(
              expandedTest === test.testId ? null : test.testId
            )}
          />
        ))}
      </div>

      {/* Thesis Value Note */}
      <div className="mt-4 pt-4 border-t border-[#30363D]">
        <p className="text-xs text-[#8B949E] italic">
          💡 <strong className="text-[#E6EDF3]">Thesis Value:</strong> Diese Evidence Matrix beweist,
          dass das Neuro-Symbolische System nicht nur "so tut als ob", sondern wirklich funktioniert.
          Die Tests zeigen topologisches Bewusstsein, State Persistence und automatische Cascade-Berechnung.
        </p>
      </div>
    </div>
  );
}

function TestResultCard({
  test,
  isExpanded,
  onToggle,
}: {
  test: TestResult;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="rounded border border-[#30363D] bg-[#090C10] overflow-hidden">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full text-left p-3 hover:bg-[#161B22] transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
              test.passed
                ? 'bg-[#2CB67D] text-white'
                : 'bg-[#E53170] text-white'
            }`}>
              {test.passed ? '✓' : '✗'}
            </div>
            <div>
              <div className="text-xs font-semibold text-[#E6EDF3]">
                {test.testId}: {test.testName}
              </div>
              <div className="text-xs text-[#8B949E] mt-0.5">
                {test.hypothesis}
              </div>
            </div>
          </div>
          <div className="text-xs text-[#8B949E]">
            {isExpanded ? '▼' : '▶'}
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-[#30363D] p-3 space-y-2 bg-[#161B22]">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-[#8B949E]">Aktion:</span>
              <p className="text-[#E6EDF3] mt-0.5">{test.action}</p>
            </div>
            <div>
              <span className="text-[#8B949E]">System-Reaktion:</span>
              <p className="text-[#E6EDF3] mt-0.5">{test.systemReaction}</p>
            </div>
          </div>

          {/* Evidence Logs */}
          <div className="mt-3">
            <span className="text-xs font-semibold text-[#8B949E] mb-2 block">
              Evidence Logs:
            </span>
            <div className="max-h-48 overflow-y-auto space-y-1 font-mono text-xs">
              {test.evidence.map((evidence, idx) => (
                <div
                  key={idx}
                  className={`p-2 rounded ${
                    evidence.startsWith('✅')
                      ? 'bg-[#2CB67D]/10 text-[#2CB67D]'
                      : evidence.startsWith('❌')
                      ? 'bg-[#E53170]/10 text-[#E53170]'
                      : evidence.startsWith('⚠️')
                      ? 'bg-[#D29922]/10 text-[#D29922]'
                      : 'bg-[#30363D] text-[#8B949E]'
                  }`}
                >
                  {evidence}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

