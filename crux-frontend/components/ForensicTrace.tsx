'use client';

import { useEffect, useRef, useState } from 'react';
import { useCruxStore, CriticLog } from '@/lib/store';
import { cruxAPI } from '@/lib/api';
import { cn } from '@/lib/utils';

interface LogEntryProps {
  log: CriticLog;
}

function LogEntry({ log }: LogEntryProps) {
  const getEventTypeColor = (eventType: string): string => {
    switch (eventType) {
      case 'DRAFT':
        return 'text-[#7F5AF0]'; // Neural Violet (Spec)
      case 'CRITIC':
        return 'text-[#D29922]'; // Warning Amber
      case 'REFINED':
        return 'text-[#2CB67D]'; // Symbolic Green (Spec)
      default:
        return 'text-[#8B949E]';
    }
  };
  
  const getEventTypeBg = (eventType: string): string => {
    switch (eventType) {
      case 'DRAFT':
        return 'bg-[#7F5AF0]/10';
      case 'CRITIC':
        return 'bg-[#D29922]/10';
      case 'REFINED':
        return 'bg-[#2CB67D]/10';
      default:
        return '';
    }
  };

  const getEventTypePrefix = (eventType: string): string => {
    switch (eventType) {
      case 'DRAFT':
        return '[DRAFT]';
      case 'CRITIC':
        return '[CRITIC]';
      case 'REFINED':
        return '[REFINED]';
      default:
        return '[LOG]';
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('de-DE', { hour12: false });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className={cn(
      "font-data space-y-1 border-b border-[#30363D]/30 py-2 text-xs transition-colors",
      getEventTypeBg(log.event_type)
    )}>
      <div className="flex items-center gap-2">
        <span className="text-[#8B949E] font-mono">{formatTimestamp(log.timestamp)}</span>
        <span className={cn(
          'font-bold px-2 py-0.5 rounded',
          getEventTypeColor(log.event_type),
          getEventTypeBg(log.event_type)
        )}>
          {getEventTypePrefix(log.event_type)}
        </span>
        <span className="text-[#8B949E] font-mono">Inject {log.inject_id}</span>
      </div>
      <div className="pl-4 text-[#E6EDF3] font-mono">{log.message}</div>
      {log.details?.validation && (
        <div className="pl-4">
          {log.details.validation.errors.length > 0 && (
            <div className="mt-1 space-y-0.5">
              {log.details.validation.errors.map((error, idx) => (
                <div key={idx} className="text-[#E53170] font-mono">
                  <span className="text-[#E53170]">✗</span> {error}
                </div>
              ))}
            </div>
          )}
          {log.details.validation.warnings.length > 0 && (
            <div className="mt-1 space-y-0.5">
              {log.details.validation.warnings.map((warning, idx) => (
                <div key={idx} className="text-[#D29922] font-mono">
                  <span className="text-[#D29922]">⚠</span> {warning}
                </div>
              ))}
            </div>
          )}
          {log.details.validation.is_valid && log.details.validation.errors.length === 0 && (
            <div className="mt-1 text-[#2CB67D] font-mono">
              <span className="text-[#2CB67D]">✓</span> Validierung erfolgreich
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ForensicTrace() {
  const { criticLogs, setCriticLogs } = useCruxStore();
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new logs arrive
  const logContainerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [criticLogs]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.jsonl')) {
      setUploadError('Datei muss eine .jsonl Datei sein');
      return;
    }

    setUploading(true);
    setUploadError(null);

    try {
      const result = await cruxAPI.uploadForensicTrace(file);
      
      // Konvertiere die hochgeladenen Logs in das CriticLog-Format
      const convertedLogs: CriticLog[] = result.logs.map((log: any) => ({
        timestamp: log.timestamp,
        inject_id: log.inject_id,
        event_type: log.event_type as 'DRAFT' | 'CRITIC' | 'REFINED',
        message: log.message,
        details: {
          validation: log.details?.validation ? {
            is_valid: log.details.validation.is_valid,
            errors: log.details.validation.errors || [],
            warnings: log.details.validation.warnings || [],
          } : undefined,
        },
      }));

      // Setze die Logs im Store
      setCriticLogs(convertedLogs);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      console.error('Error uploading forensic trace:', error);
      setUploadError(error.message || 'Fehler beim Hochladen der Datei');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-[#090C10] min-h-0">
      <div className="border-b border-[#30363D] p-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-[#E6EDF3]">Forensic Trace & Critic Logs</h2>
            <p className="text-sm text-[#8B949E]">Transparenz der Agenten-Entscheidungen</p>
          </div>
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".jsonl"
              onChange={handleFileUpload}
              className="hidden"
              id="forensic-upload"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="rounded border border-[#30363D] bg-[#161B22] px-3 py-1 text-xs text-[#8B949E] hover:text-[#E6EDF3] hover:bg-[#30363D] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <span className="h-3 w-3 animate-spin rounded-full border-2 border-[#8B949E] border-t-transparent" />
                  Lade hoch...
                </>
              ) : (
                '📤 Upload .jsonl'
              )}
            </button>
          </div>
        </div>
        {uploadError && (
          <div className="mt-3 p-3 bg-[#E53170]/10 border border-[#E53170] rounded-md">
            <p className="text-sm text-[#E53170]">{uploadError}</p>
          </div>
        )}
      </div>
      <div ref={logContainerRef} className="terminal-bg flex-1 overflow-y-auto p-4 font-data">
        {criticLogs.length === 0 ? (
          <div className="flex h-full items-center justify-center text-[#8B949E]">
            <div className="text-center">
              <p className="text-sm">Keine Logs vorhanden</p>
              <p className="mt-2 text-xs">Critic-Logs erscheinen hier während der Generierung</p>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {criticLogs.map((log, idx) => (
              <LogEntry key={idx} log={log} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

