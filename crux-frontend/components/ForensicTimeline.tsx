'use client';

import { useMemo } from 'react';
import { useCruxStore } from '@/lib/store';
import { parseTimeOffset } from '@/lib/utils';

/**
 * Forensic Timeline: Chronologische Darstellung aller Injects und Validierungen
 * 
 * Zeigt:
 * - Alle Injects in chronologischer Reihenfolge
 * - Critic Agent Validierungen
 * - Entscheidungspunkte (Interactive Mode)
 * - Kausalitäten (Ursache -> Wirkung)
 */
export default function ForensicTimeline() {
  const { injects, criticLogs, graphTimeOffset } = useCruxStore();

  // Kombiniere Injects und Critic Logs chronologisch
  const timelineEvents = useMemo(() => {
    const events: Array<{
      id: string;
      timestamp: string;
      timeOffset: string;
      type: 'inject' | 'validation' | 'decision';
      data: any;
    }> = [];

    // Füge Injects hinzu
    injects.forEach(inject => {
      events.push({
        id: inject.inject_id,
        timestamp: inject.created_at?.toString() || '',
        timeOffset: inject.time_offset,
        type: 'inject',
        data: inject,
      });
    });

    // Füge Critic Validierungen hinzu
    criticLogs.forEach(log => {
      if (log.details?.validation) {
        events.push({
          id: `critic-${log.inject_id}`,
          timestamp: log.timestamp,
          timeOffset: '', // Wird aus Inject abgeleitet
          type: 'validation',
          data: log,
        });
      }
    });

    // Sortiere chronologisch nach timeOffset
    events.sort((a, b) => {
      const timeA = parseTimeOffset(a.timeOffset || 'T+00:00');
      const timeB = parseTimeOffset(b.timeOffset || 'T+00:00');
      return timeA - timeB;
    });

    return events;
  }, [injects, criticLogs]);

  const currentTime = parseTimeOffset(graphTimeOffset);

  return (
    <div className="rounded border border-[#30363D] bg-[#161B22] p-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[#E6EDF3] mb-1">
          Forensic Timeline
        </h3>
        <p className="text-xs text-[#8B949E]">
          Chronologische Darstellung aller Events und Validierungen
        </p>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {timelineEvents.length === 0 ? (
          <p className="text-xs text-[#8B949E] text-center py-8">
            Keine Events verfügbar
          </p>
        ) : (
          timelineEvents.map((event, index) => {
            const eventTime = parseTimeOffset(event.timeOffset || 'T+00:00');
            const isPast = eventTime <= currentTime;
            const isCurrent = Math.abs(eventTime - currentTime) < 5; // 5 Minuten Toleranz

            return (
              <div
                key={event.id}
                className={`relative pl-6 border-l-2 ${
                  isCurrent
                    ? 'border-[#7F5AF0]'
                    : isPast
                    ? 'border-[#2CB67D]'
                    : 'border-[#30363D]'
                }`}
              >
                {/* Timeline Dot */}
                <div
                  className={`absolute left-0 top-2 w-3 h-3 rounded-full -translate-x-[7px] ${
                    isCurrent
                      ? 'bg-[#7F5AF0] ring-2 ring-[#7F5AF0] ring-opacity-50'
                      : isPast
                      ? 'bg-[#2CB67D]'
                      : 'bg-[#30363D]'
                  }`}
                />

                {/* Event Content */}
                <div
                  className={`rounded border p-3 ${
                    isCurrent
                      ? 'border-[#7F5AF0] bg-[#7F5AF0]/10'
                      : isPast
                      ? 'border-[#30363D] bg-[#090C10]'
                      : 'border-[#30363D] bg-[#090C10] opacity-50'
                  }`}
                >
                  {/* Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {event.type === 'inject' && (
                        <span className="text-xs font-semibold text-[#E6EDF3]">
                          📨 {event.data.inject_id}
                        </span>
                      )}
                      {event.type === 'validation' && (
                        <span className="text-xs font-semibold text-[#E6EDF3]">
                          ✅ Validation
                        </span>
                      )}
                      {event.type === 'decision' && (
                        <span className="text-xs font-semibold text-[#E6EDF3]">
                          🎮 Decision
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-data text-[#8B949E]">
                      {event.timeOffset}
                    </span>
                  </div>

                  {/* Content */}
                  {event.type === 'inject' && (
                    <div>
                      <p className="text-xs text-[#E6EDF3] mb-1">
                        {event.data.content.substring(0, 100)}
                        {event.data.content.length > 100 && '...'}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs text-[#8B949E]">
                          Phase: {event.data.phase}
                        </span>
                        {event.data.technical_metadata?.mitre_id && (
                          <span className="text-xs text-[#8B949E]">
                            MITRE: {event.data.technical_metadata.mitre_id}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {event.type === 'validation' && (
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`text-xs font-semibold ${
                            event.data.details?.validation?.is_valid
                              ? 'text-[#2CB67D]'
                              : 'text-[#E53170]'
                          }`}
                        >
                          {event.data.details?.validation?.is_valid
                            ? '✓ Valid'
                            : '✗ Invalid'}
                        </span>
                      </div>
                      {event.data.details?.validation?.errors?.length > 0 && (
                        <div className="mt-1">
                          {event.data.details.validation.errors.map(
                            (error: string, idx: number) => (
                              <p
                                key={idx}
                                className="text-xs text-[#E53170]"
                              >
                                • {error}
                              </p>
                            )
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

