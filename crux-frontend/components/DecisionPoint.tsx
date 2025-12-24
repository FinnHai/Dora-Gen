'use client';

import { useState } from 'react';

/**
 * Decision Point: Human-in-the-Loop Komponente
 * 
 * Zeigt Entscheidungsoptionen an und ermöglicht dem Nutzer,
 * den Verlauf des Szenarios zu beeinflussen.
 */
interface DecisionOption {
  id: string;
  title: string;
  description: string;
  type: string;
  impact?: {
    phase_change?: string;
    asset_protection?: string;
    response_effectiveness?: string;
    outcome?: string;
  };
}

interface DecisionPointProps {
  decisionId: string;
  question: string;
  context: string;
  options: DecisionOption[];
  onDecision: (optionId: string) => void;
}

export default function DecisionPoint({
  decisionId,
  question,
  context,
  options,
  onDecision,
}: DecisionPointProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-2xl mx-4 rounded-lg border border-[#30363D] bg-[#161B22] p-6 shadow-2xl">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🎮</span>
            <h2 className="text-lg font-semibold text-[#E6EDF3]">
              Decision Point
            </h2>
          </div>
          <p className="text-sm text-[#8B949E]">{context}</p>
        </div>

        {/* Question */}
        <div className="mb-6 p-4 rounded border border-[#7F5AF0] bg-[#7F5AF0]/10">
          <p className="text-base font-semibold text-[#E6EDF3]">{question}</p>
        </div>

        {/* Options */}
        <div className="space-y-3 mb-6">
          {options.map((option) => (
            <button
              key={option.id}
              onClick={() => setSelectedOption(option.id)}
              className={`w-full text-left p-4 rounded border transition-all ${
                selectedOption === option.id
                  ? 'border-[#7F5AF0] bg-[#7F5AF0]/20'
                  : 'border-[#30363D] bg-[#090C10] hover:border-[#7F5AF0]/50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-[#E6EDF3] mb-1">
                    {option.title}
                  </h3>
                  <p className="text-xs text-[#8B949E] mb-2">
                    {option.description}
                  </p>
                  {option.impact && (
                    <div className="mt-2 space-y-1">
                      {option.impact.outcome && (
                        <p className="text-xs text-[#D29922] italic">
                          ⚠️ {option.impact.outcome}
                        </p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-[#8B949E]">
                        {option.impact.asset_protection && (
                          <span>
                            🛡️ Protection: {option.impact.asset_protection}
                          </span>
                        )}
                        {option.impact.response_effectiveness && (
                          <span>
                            ⚡ Effectiveness:{' '}
                            {option.impact.response_effectiveness}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                <div
                  className={`ml-4 w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    selectedOption === option.id
                      ? 'border-[#7F5AF0] bg-[#7F5AF0]'
                      : 'border-[#30363D]'
                  }`}
                >
                  {selectedOption === option.id && (
                    <svg
                      className="w-3 h-3 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3">
          <button
            onClick={() => onDecision(selectedOption || options[0].id)}
            disabled={!selectedOption}
            className={`px-4 py-2 rounded text-sm font-semibold transition-colors ${
              selectedOption
                ? 'bg-[#7F5AF0] text-white hover:bg-[#6D4DD4]'
                : 'bg-[#30363D] text-[#8B949E] cursor-not-allowed'
            }`}
          >
            Entscheidung treffen
          </button>
        </div>
      </div>
    </div>
  );
}

