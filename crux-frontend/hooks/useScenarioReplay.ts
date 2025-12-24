/**
 * Scenario Replay Hook: Replay Timeline Events auf Graph Topology
 * 
 * Diese Hook ermöglicht es, den Graph-Zustand zu einem bestimmten Zeitpunkt
 * zu rekonstruieren, indem sie Events aus der Timeline "replayt".
 */

import { useMemo } from 'react';
import { GraphNode, Inject } from '@/lib/store';
import { parseTimeOffset } from '@/lib/utils';

/**
 * Replay Timeline Events auf Graph Nodes
 * 
 * @param initialNodes - Die Basis-Topology (Ground Truth aus Neo4j)
 * @param events - Timeline Events (Injects) die auf die Nodes angewendet werden sollen
 * @param sliderTime - Der aktuelle Zeitpunkt (z.B. "T+01:30")
 * @returns Nodes mit aktualisiertem Status basierend auf Events bis zum sliderTime
 */
export function useScenarioReplay(
  initialNodes: GraphNode[],
  events: Inject[],
  sliderTime: string
): GraphNode[] {
  return useMemo(() => {
    // Starte mit sauberer Kopie der initialen Topology
    let currentNodes = initialNodes.map(node => ({ ...node }));

    // Parse slider time zu Minuten
    const currentTimeMinutes = parseTimeOffset(sliderTime);

    // Filtere Events die VOR dem sliderTime passiert sind
    const pastEvents = events.filter(event => {
      const eventTime = parseTimeOffset(event.time_offset);
      return eventTime <= currentTimeMinutes;
    });

    // Replay jedes Event auf die Nodes
    pastEvents.forEach(event => {
      // Prüfe ob Event Assets betrifft
      if (event.affected_assets && event.affected_assets.length > 0) {
        event.affected_assets.forEach(assetId => {
          const targetNodeIndex = currentNodes.findIndex(n => n.id === assetId);
          
          if (targetNodeIndex !== -1) {
            const node = currentNodes[targetNodeIndex];
            
            // Bestimme neuen Status basierend auf Event-Content
            const contentLower = event.content.toLowerCase();
            
            if (
              contentLower.includes('compromised') ||
              contentLower.includes('encrypted') ||
              contentLower.includes('breach') ||
              contentLower.includes('ransomware')
            ) {
              node.status = 'compromised';
            } else if (
              contentLower.includes('degraded') ||
              contentLower.includes('suspicious') ||
              contentLower.includes('anomaly')
            ) {
              // Nur auf degraded setzen wenn nicht schon compromised
              if (node.status !== 'compromised') {
                node.status = 'degraded';
              }
            } else if (
              contentLower.includes('offline') ||
              contentLower.includes('down') ||
              contentLower.includes('unavailable')
            ) {
              // Nur auf offline setzen wenn nicht schon compromised oder degraded
              if (node.status !== 'compromised' && node.status !== 'degraded') {
                node.status = 'offline';
              }
            }
            
            // Speichere Referenz zum letzten Inject für Debugging
            // (kann später für Tooltips verwendet werden)
            (node as any).lastInject = event.inject_id;
          }
        });
      }
    });

    return currentNodes;
  }, [initialNodes, events, sliderTime]);
}

/**
 * Berechnet welche Edges als "Attack Vector" markiert werden sollen
 * (Cascading Failure Lines)
 */
export function calculateAttackVectors(
  nodes: GraphNode[],
  events: Inject[],
  sliderTime: string
): Set<string> {
  const attackVectorEdges = new Set<string>();
  const currentTimeMinutes = parseTimeOffset(sliderTime);

  // Finde kompromittierte Nodes
  const compromisedNodeIds = new Set(
    nodes.filter(n => n.status === 'compromised').map(n => n.id)
  );

  // Finde Events die zu Kompromittierung geführt haben
  const compromiseEvents = events.filter(event => {
    const eventTime = parseTimeOffset(event.time_offset);
    return eventTime <= currentTimeMinutes && 
           event.affected_assets.some(assetId => compromisedNodeIds.has(assetId));
  });

  // Markiere Edges die von kompromittierten Nodes ausgehen als Attack Vectors
  // (Dies wird später in der Edge-Komponente verwendet)
  compromiseEvents.forEach(event => {
    event.affected_assets.forEach(assetId => {
      if (compromisedNodeIds.has(assetId)) {
        // Alle ausgehenden Edges von diesem Node sind potentielle Attack Vectors
        // (Wird in der Hauptkomponente verwendet)
        attackVectorEdges.add(assetId);
      }
    });
  });

  return attackVectorEdges;
}

