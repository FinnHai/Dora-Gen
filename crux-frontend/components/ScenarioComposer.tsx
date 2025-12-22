'use client';

import { useCruxStore, Inject, InjectStatus } from '@/lib/store';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useState } from 'react';

interface InjectCardProps {
  inject: Inject;
  isSelected: boolean;
  onClick: () => void;
  highlightedNodeId: string | null;
  setHoveredAsset: (assetId: string | null) => void;
  setHighlightedNode: (nodeId: string | null) => void;
}

function InjectCard({ inject, isSelected, onClick, highlightedNodeId, setHoveredAsset, setHighlightedNode }: InjectCardProps) {
  const getStatusColor = (status: InjectStatus): string => {
    switch (status) {
      case 'generating':
        return '#7F5AF0'; // Neural Violet (Spec)
      case 'validating':
        return '#D29922'; // Warning Amber
      case 'verified':
        return '#2CB67D'; // Symbolic Green (Spec)
      case 'rejected':
        return '#E53170'; // Intervention Red (Spec)
      default:
        return '#8B949E';
    }
  };
  
  const getBorderColor = (status: InjectStatus): string => {
    return getStatusColor(status);
  };

  const getStatusLabel = (status: InjectStatus): string => {
    switch (status) {
      case 'generating':
        return 'Generierend';
      case 'validating':
        return 'Validierend';
      case 'verified':
        return 'Verifiziert';
      case 'rejected':
        return 'Abgelehnt';
      default:
        return 'Unbekannt';
    }
  };

  const borderColor = getBorderColor(inject.status);
  const hasError = inject.status === 'validating' && inject.refinement_history && inject.refinement_history.length > 0;

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all',
        `border-2`,
        isSelected && 'shadow-lg',
        inject.status === 'generating' && 'border-[#7F5AF0] hover:border-[#7F5AF0]/70',
        inject.status === 'validating' && hasError && 'border-[#E53170] animate-pulse-error',
        inject.status === 'verified' && 'border-[#2CB67D]',
        inject.status === 'rejected' && 'border-[#E53170]',
        !isSelected && inject.status !== 'generating' && inject.status !== 'validating' && inject.status !== 'verified' && inject.status !== 'rejected' && 'border-[#30363D] hover:border-[#7F5AF0]/50',
        isSelected && `shadow-[${borderColor}]/20`
      )}
      style={{
        borderColor: borderColor,
        boxShadow: isSelected ? `0 10px 15px -3px ${borderColor}20, 0 4px 6px -2px ${borderColor}10` : undefined,
      }}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-data text-sm text-[#8B949E]">{inject.inject_id}</span>
            <span className="font-data text-xs text-[#8B949E]">{inject.time_offset}</span>
          </div>
          <div
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: getStatusColor(inject.status) }}
            title={getStatusLabel(inject.status)}
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-sm">
            <span className="font-semibold">{inject.source}</span>
            <span className="text-[#8B949E]"> → </span>
            <span className="text-[#8B949E]">{inject.target}</span>
          </div>
          <div className="text-xs text-[#8B949E]">{inject.modality}</div>
          <div className="relative">
            <div
              className={cn(
                'text-sm leading-relaxed transition-all duration-500',
                inject.status === 'generating' && 'text-[#7F5AF0]',
                inject.status === 'validating' && 'text-[#E53170]',
                inject.status === 'verified' && 'text-[#E6EDF3]',
                inject.status === 'rejected' && 'line-through text-[#8B949E]'
              )}
            >
              {inject.content.split(' ').map((word, idx) => {
                // Highlight halluzinierte Assets (z.B. SRV-PAY-99)
                const isHallucinated = word.includes('SRV-PAY-99') || word.includes('SRV-Backup-99');
                return (
                  <span
                    key={idx}
                    className={cn(
                      inject.status === 'validating' && isHallucinated && 'text-[#E53170] underline decoration-2 animate-pulse-error font-bold'
                    )}
                  >
                    {word}{' '}
                  </span>
                );
              })}
            </div>
            {inject.status === 'generating' && (
              <div className="absolute right-0 top-0">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#7F5AF0] border-t-transparent" />
              </div>
            )}
            {inject.status === 'verified' && (
              <div className="absolute right-0 top-0">
                <svg className="h-4 w-4 text-[#2CB67D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
          </div>
          {inject.refinement_history && inject.refinement_history.length > 0 && (
            <div className="mt-2 space-y-2 border-t border-[#30363D] pt-2">
              {inject.refinement_history.map((refinement, idx) => (
                <div key={idx} className="text-xs">
                  <div className="text-critical line-through opacity-60">
                    {refinement.original}
                  </div>
                  <div className="text-verified mt-1">→ {refinement.corrected}</div>
                  {refinement.errors.length > 0 && (
                    <div className="mt-1 space-y-0.5 text-critical">
                      {refinement.errors.map((error, errIdx) => (
                        <div key={errIdx} className="text-[10px]">✗ {error}</div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          {inject.affected_assets.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {inject.affected_assets.map((asset) => (
                <span
                  key={asset}
                  className={cn(
                    "font-data rounded px-2 py-0.5 text-xs transition-colors cursor-pointer",
                    highlightedNodeId === asset
                      ? "bg-[#7E57C2]/30 text-[#7E57C2]"
                      : "bg-[#30363D] text-[#8B949E] hover:bg-[#7E57C2]/20 hover:text-[#7E57C2]"
                  )}
                  onMouseEnter={() => {
                    setHoveredAsset(asset);
                    setHighlightedNode(asset);
                  }}
                  onMouseLeave={() => {
                    setHoveredAsset(null);
                    setHighlightedNode(null);
                  }}
                >
                  {asset}
                </span>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function ScenarioComposer() {
  const { injects, selectedInjectId, selectInject, setHoveredAsset, highlightedNodeId, setHighlightedNode } = useCruxStore();

  return (
    <div className="flex h-full flex-col bg-[#090C10]">
      <div className="border-b border-[#30363D] p-4">
        <h2 className="text-lg font-semibold text-[#E6EDF3]">Scenario Composer</h2>
        <p className="text-sm text-[#8B949E]">Timeline der generierten Injects</p>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {injects.length === 0 ? (
          <div className="flex h-full items-center justify-center text-[#8B949E]">
            <div className="text-center">
              <p className="text-sm">Noch keine Injects generiert</p>
              <p className="mt-2 text-xs">Starte eine Simulation, um Injects zu sehen</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {injects.map((inject) => (
              <InjectCard
                key={inject.inject_id}
                inject={inject}
                isSelected={selectedInjectId === inject.inject_id}
                onClick={() => selectInject(inject.inject_id)}
                highlightedNodeId={highlightedNodeId}
                setHoveredAsset={setHoveredAsset}
                setHighlightedNode={setHighlightedNode}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

