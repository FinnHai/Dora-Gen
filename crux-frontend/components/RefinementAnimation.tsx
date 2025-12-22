'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface RefinementAnimationProps {
  original: string;
  corrected: string;
  errors: string[];
  onComplete?: () => void;
}

export default function RefinementAnimation({
  original,
  corrected,
  errors,
  onComplete,
}: RefinementAnimationProps) {
  const [phase, setPhase] = useState<'ghost' | 'detect' | 'correct' | 'finalize'>('ghost');
  const [showCorrection, setShowCorrection] = useState(false);

  useEffect(() => {
    // Phase 1: Ghosting (violet)
    const timer1 = setTimeout(() => {
      setPhase('detect');
    }, 500);

    // Phase 2: Detection (red underline)
    const timer2 = setTimeout(() => {
      setPhase('correct');
      setShowCorrection(true);
    }, 1500);

    // Phase 3: Correction (strike through + green replacement)
    const timer3 = setTimeout(() => {
      setPhase('finalize');
    }, 3000);

    // Phase 4: Finalize (white text + green checkmark)
    const timer4 = setTimeout(() => {
      if (onComplete) onComplete();
    }, 4000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, [onComplete]);

  return (
    <div className="relative space-y-2">
      {/* Phase 1-3: Original text with animation */}
      <div
        className={cn(
          'transition-all duration-500',
          phase === 'ghost' && 'text-neural',
          phase === 'detect' && 'text-neural underline decoration-critical decoration-2',
          phase === 'correct' && 'text-neural line-through',
          phase === 'finalize' && 'text-[#E6EDF3]'
        )}
      >
        {original}
      </div>

      {/* Phase 3-4: Corrected text */}
      {showCorrection && (
        <div
          className={cn(
            'transition-all duration-500',
            phase === 'correct' && 'text-verified animate-in slide-in-from-left',
            phase === 'finalize' && 'text-[#E6EDF3]'
          )}
        >
          → {corrected}
        </div>
      )}

      {/* Phase 4: Green checkmark */}
      {phase === 'finalize' && (
        <div className="flex items-center gap-2 text-verified">
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
          <span className="text-xs">Verifiziert</span>
        </div>
      )}

      {/* Error details */}
      {errors.length > 0 && phase !== 'finalize' && (
        <div className="mt-2 space-y-1 text-xs text-critical">
          {errors.map((error, idx) => (
            <div key={idx}>✗ {error}</div>
          ))}
        </div>
      )}
    </div>
  );
}

