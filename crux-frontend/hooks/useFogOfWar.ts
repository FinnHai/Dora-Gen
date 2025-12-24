/**
 * Fog of War Hook: Berechnet "Perceived State" basierend auf verfügbaren Informationen
 * 
 * Im Gegensatz zu "God Mode" (Ground Truth) zeigt Fog of War nur das, was
 * der Manager basierend auf Alerts und Investigationen sehen würde.
 */

import { useMemo } from 'react';
import { GraphNode, Inject } from '@/lib/store';
import { parseTimeOffset } from '@/lib/utils';

/**
 * Berechnet den "Perceived State" eines Nodes basierend auf verfügbaren Informationen
 */
/**
 * UX View Mode Hook: Berechnet "Perceived State" basierend auf View Mode
 * 
 * 🛡️ Player Mode: Manager-Sicht (Fog of War - Perceived State)
 *    - Zeigt nur was durch Alerts/Investigations bekannt ist
 *    - Assets bleiben grün bis Alert/Investigation
 *    - Simuliert Unsicherheit und Stress
 * 
 * 👁️ God Mode: Trainer-Sicht (Ground Truth - Actual State)
 *    - Zeigt Ground Truth direkt aus Neo4j
 *    - Alle kompromittierten Nodes sofort sichtbar
 *    - Für Debugging und Debriefing
 */
export function useFogOfWar(
  nodes: GraphNode[],
  events: Inject[],
  sliderTime: string,
  viewMode: 'player' | 'god'
): GraphNode[] {
  return useMemo(() => {
    // 👁️ God Mode: Zeige Ground Truth (alles sichtbar)
    if (viewMode === 'god') {
      return nodes;
    }

    // 🛡️ Player Mode: Zeige nur was durch Alerts/Investigationen bekannt ist
    const currentTimeMinutes = parseTimeOffset(sliderTime);
    const perceivedNodes = nodes.map(node => ({ ...node }));

    // Finde alle Events die Alerts/Investigationen enthalten
    const pastEvents = events.filter(event => {
      const eventTime = parseTimeOffset(event.time_offset);
      return eventTime <= currentTimeMinutes;
    });

    // Gruppiere Events nach Asset
    const assetKnowledge: Record<string, {
      hasAlert: boolean;
      isInvestigated: boolean;
      confirmedStatus?: GraphNode['status'];
      alertTime?: number;
    }> = {};

    pastEvents.forEach(event => {
      // Prüfe ob Event ein Alert ist (SIEM, IDS, etc.)
      const isAlert = event.modality?.toLowerCase().includes('alert') ||
                     event.modality?.toLowerCase().includes('siem') ||
                     event.modality?.toLowerCase().includes('ids') ||
                     event.content.toLowerCase().includes('alert') ||
                     event.content.toLowerCase().includes('detected');

      // Prüfe ob Event eine Investigation ist
      const isInvestigation = event.modality?.toLowerCase().includes('investigation') ||
                             event.content.toLowerCase().includes('investigated') ||
                             event.content.toLowerCase().includes('confirmed');

      event.affected_assets.forEach(assetId => {
        if (!assetKnowledge[assetId]) {
          assetKnowledge[assetId] = {
            hasAlert: false,
            isInvestigated: false,
          };
        }

        const eventTime = parseTimeOffset(event.time_offset);
        
        if (isAlert && !assetKnowledge[assetId].hasAlert) {
          assetKnowledge[assetId].hasAlert = true;
          assetKnowledge[assetId].alertTime = eventTime;
        }

        if (isInvestigation) {
          assetKnowledge[assetId].isInvestigated = true;
          
          // Bestimme bestätigten Status aus Investigation
          const contentLower = event.content.toLowerCase();
          if (contentLower.includes('compromised') || contentLower.includes('breach')) {
            assetKnowledge[assetId].confirmedStatus = 'compromised';
          } else if (contentLower.includes('degraded') || contentLower.includes('suspicious')) {
            assetKnowledge[assetId].confirmedStatus = 'degraded';
          } else if (contentLower.includes('offline')) {
            assetKnowledge[assetId].confirmedStatus = 'offline';
          } else {
            assetKnowledge[assetId].confirmedStatus = 'online';
          }
        }
      });
    });

    // Wende Fog of War Logik an
    perceivedNodes.forEach(node => {
      const knowledge = assetKnowledge[node.id];

      if (!knowledge) {
        // Keine Informationen verfügbar: Zeige als "unknown" (grau/transparent)
        node.status = 'online'; // Standard, aber wird visuell anders dargestellt
        (node as any).fogOfWar = 'unknown';
      } else if (knowledge.isInvestigated && knowledge.confirmedStatus) {
        // Investigation durchgeführt: Zeige bestätigten Status
        node.status = knowledge.confirmedStatus;
        (node as any).fogOfWar = 'confirmed';
      } else if (knowledge.hasAlert) {
        // Alert vorhanden, aber noch nicht investigiert: Zeige als "suspicious"
        node.status = 'degraded';
        (node as any).fogOfWar = 'alert';
      } else {
        // Keine Alerts: Zeige als normal (könnte aber trotzdem kompromittiert sein)
        node.status = 'online';
        (node as any).fogOfWar = 'normal';
      }
    });

    return perceivedNodes;
  }, [nodes, events, sliderTime, viewMode]);
}

