'use client';

import { useCruxStore } from '@/lib/store';

/**
 * Mode Indicator: Zeigt aktuelle UX- und Backend-Modi
 * 
 * Trennt klar zwischen:
 * - UX View Modes (Player/God) - Konzeptionelle Sicht-Modi
 * - Backend Execution Modes (Thesis/Legacy/Interactive) - Technische Ausführungs-Modi
 */
export default function ModeIndicator() {
  const { viewMode, executionMode, interactiveMode } = useCruxStore();

  return (
    <div className="flex items-center gap-3 text-xs">
      {/* UX View Mode */}
      <div className="flex items-center gap-2 rounded border border-[#30363D] bg-[#161B22] px-2 py-1">
        <span className="text-[#8B949E]">View:</span>
        {viewMode === 'god' ? (
          <span className="flex items-center gap-1 text-[#7F5AF0]">
            <span>👁️</span>
            <span className="font-semibold">God Mode</span>
            <span className="text-[#8B949E]">(Trainer)</span>
          </span>
        ) : (
          <span className="flex items-center gap-1 text-[#2CB67D]">
            <span>🛡️</span>
            <span className="font-semibold">Player Mode</span>
            <span className="text-[#8B949E]">(Manager)</span>
          </span>
        )}
      </div>

      {/* Backend Execution Mode */}
      <div className="flex items-center gap-2 rounded border border-[#30363D] bg-[#161B22] px-2 py-1">
        <span className="text-[#8B949E]">Backend:</span>
        {executionMode === 'thesis' ? (
          <span className="flex items-center gap-1 text-[#2CB67D]">
            <span>🎓</span>
            <span className="font-semibold">Thesis Mode</span>
            <span className="text-[#8B949E]">(Full Validation)</span>
          </span>
        ) : (
          <span className="flex items-center gap-1 text-[#D29922]">
            <span>🚀</span>
            <span className="font-semibold">Legacy Mode</span>
            <span className="text-[#8B949E]">(Skip Validation)</span>
          </span>
        )}
        {interactiveMode && (
          <span className="ml-1 text-[#7F5AF0]">🎮 Interactive</span>
        )}
      </div>
    </div>
  );
}

