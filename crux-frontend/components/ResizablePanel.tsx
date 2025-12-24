'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ResizablePanelProps {
  children: React.ReactNode;
  defaultWidth: number; // Prozent
  minWidth?: number; // Prozent
  maxWidth?: number; // Prozent
  onResize?: (width: number) => void;
  className?: string;
  storageKey?: string; // Für Persistierung
}

export function ResizablePanel({
  children,
  defaultWidth,
  minWidth = 10,
  maxWidth = 90,
  onResize,
  className,
  storageKey
}: ResizablePanelProps) {
  const [width, setWidth] = useState(() => {
    if (storageKey && typeof window !== 'undefined') {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = parseFloat(saved);
        if (!isNaN(parsed) && parsed >= minWidth && parsed <= maxWidth) {
          return parsed;
        }
      }
    }
    return defaultWidth;
  });

  // Aktualisiere width wenn defaultWidth sich ändert (von außen)
  useEffect(() => {
    setWidth(defaultWidth);
  }, [defaultWidth]);

  const [isResizing, setIsResizing] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef<number>(0);
  const startWidthRef = useRef<number>(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    startXRef.current = e.clientX;
    startWidthRef.current = width;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [width]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const container = panelRef.current?.parentElement;
    if (!container) return;

    const containerWidth = container.offsetWidth;
    const deltaX = e.clientX - startXRef.current;
    const deltaPercent = (deltaX / containerWidth) * 100;
    
    let newWidth = startWidthRef.current + deltaPercent;
    
    // Stelle sicher, dass wir innerhalb der Grenzen bleiben
    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    
    // Berechne die Gesamtbreite aller Geschwister-Panels
    const siblings = Array.from(container.children) as HTMLElement[];
    const currentIndex = siblings.indexOf(panelRef.current!);
    let totalWidth = 0;
    
    siblings.forEach((sibling, index) => {
      if (index !== currentIndex) {
        const siblingWidth = parseFloat(sibling.style.width || '0');
        totalWidth += siblingWidth;
      }
    });
    
    // Stelle sicher, dass die Gesamtbreite nicht über 100% geht
    const maxAllowedWidth = 100 - totalWidth;
    newWidth = Math.min(newWidth, maxAllowedWidth);
    
    setWidth(newWidth);
    if (onResize) {
      onResize(newWidth);
    }
  }, [isResizing, minWidth, maxWidth, onResize]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
    
    // Speichere in localStorage
    if (storageKey) {
      localStorage.setItem(storageKey, width.toString());
    }
  }, [width, storageKey, handleMouseMove]);

  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  return (
    <div
      ref={panelRef}
      className={cn('relative flex-shrink-0 min-w-0', className)}
      style={{ width: `${width}%` }}
    >
      {children}
      <div
        onMouseDown={handleMouseDown}
        className={cn(
          'absolute right-0 top-0 bottom-0 w-1 cursor-col-resize z-10',
          'hover:bg-[#7F5AF0]/50 transition-colors',
          isResizing && 'bg-[#7F5AF0]'
        )}
        style={{ marginRight: '-2px' }}
      >
        <div className="absolute inset-y-0 -right-1 w-3" />
      </div>
    </div>
  );
}

interface ResizeHandleProps {
  onMouseDown: (e: React.MouseEvent) => void;
  isResizing?: boolean;
}

export function ResizeHandle({ onMouseDown, isResizing }: ResizeHandleProps) {
  return (
    <div
      onMouseDown={onMouseDown}
      className={cn(
        'w-1 cursor-col-resize z-10 flex-shrink-0',
        'hover:bg-[#7F5AF0]/50 transition-colors',
        isResizing && 'bg-[#7F5AF0]'
      )}
    >
      <div className="absolute inset-y-0 -left-1 -right-1 w-3" />
    </div>
  );
}

