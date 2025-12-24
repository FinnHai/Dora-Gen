'use client';

import { useCruxStore } from '@/lib/store';
import { Card } from '@/components/ui/card';
import { useEffect, useState } from 'react';

interface WorkflowNode {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  duration?: number;
  timestamp?: string;
}

const WORKFLOW_NODES: WorkflowNode[] = [
  { id: 'state_check', name: 'State Check', status: 'pending' },
  { id: 'manager', name: 'Manager Agent', status: 'pending' },
  { id: 'intel', name: 'Intel Agent', status: 'pending' },
  { id: 'action_selection', name: 'Action Selection', status: 'pending' },
  { id: 'generator', name: 'Generator Agent', status: 'pending' },
  { id: 'critic', name: 'Critic Agent', status: 'pending' },
  { id: 'state_update', name: 'State Update', status: 'pending' },
];

export default function WorkflowVisualization() {
  const { selectedInjectId, injects } = useCruxStore();
  const [nodes, setNodes] = useState<WorkflowNode[]>(WORKFLOW_NODES);
  const [currentIteration, setCurrentIteration] = useState(0);
  
  // Simuliere Workflow-Status basierend auf Inject
  useEffect(() => {
    if (!selectedInjectId) {
      setNodes(WORKFLOW_NODES.map(n => ({ ...n, status: 'pending' as const })));
      return;
    }
    
    const inject = injects.find(inj => inj.inject_id === selectedInjectId);
    if (!inject) return;
    
    // Simuliere Workflow-Status basierend auf Inject-Status
    const statusMap: Record<string, 'completed' | 'running' | 'error'> = {
      'verified': 'completed',
      'validating': 'running',
      'generating': 'running',
      'rejected': 'error'
    };
    
    const injectStatus = statusMap[inject.status] || 'completed';
    
    // Setze alle Nodes bis zum aktuellen Status
    setNodes(prevNodes => {
      const currentIndex = prevNodes.findIndex(n => n.id === 'critic');
      return prevNodes.map((node, idx) => {
        if (idx < currentIndex) {
          return { ...node, status: 'completed' as const };
        } else if (idx === currentIndex) {
          return { ...node, status: injectStatus };
        } else {
          return { ...node, status: 'pending' as const };
        }
      });
    });
  }, [selectedInjectId, injects]);
  
  return (
    <Card className="p-6 bg-panel border border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">⚙️ Workflow Visualization</h3>
        <div className="text-xs text-gray-400 font-mono">
          Iteration: {currentIteration}
        </div>
      </div>
      
      {/* Workflow-Nodes */}
      <div className="space-y-3">
        {nodes.map((node, idx) => (
          <div key={node.id} className="relative">
            {/* Verbindungslinie */}
            {idx > 0 && (
              <div className={`absolute left-6 -top-3 w-0.5 h-3 ${
                nodes[idx - 1].status === 'completed' ? 'bg-symbolic' :
                nodes[idx - 1].status === 'error' ? 'bg-intervention' :
                'bg-gray-700'
              }`} />
            )}
            
            {/* Node */}
            <div className={`flex items-center gap-4 p-3 rounded border ${
              node.status === 'completed' 
                ? 'bg-symbolic/10 border-symbolic/30' 
                : node.status === 'running'
                ? 'bg-neuro/10 border-neuro/30'
                : node.status === 'error'
                ? 'bg-intervention/10 border-intervention/30'
                : 'bg-void border-gray-800'
            }`}>
              {/* Status-Indikator */}
              <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                node.status === 'completed' ? 'bg-symbolic' :
                node.status === 'running' ? 'bg-neuro animate-pulse' :
                node.status === 'error' ? 'bg-intervention' :
                'bg-gray-600'
              }`} />
              
              {/* Node-Info */}
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-mono ${
                    node.status === 'completed' ? 'text-symbolic' :
                    node.status === 'running' ? 'text-neuro' :
                    node.status === 'error' ? 'text-intervention' :
                    'text-gray-400'
                  }`}>
                    {node.name}
                  </span>
                  {node.duration && (
                    <span className="text-xs text-gray-500 font-mono">
                      {node.duration < 1000 ? `${node.duration}ms` : `${(node.duration / 1000).toFixed(1)}s`}
                    </span>
                  )}
                </div>
                {node.timestamp && (
                  <div className="text-xs text-gray-600 font-mono mt-1">
                    {new Date(node.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
              
              {/* Status-Icon */}
              {node.status === 'completed' && (
                <span className="text-symbolic text-sm">✓</span>
              )}
              {node.status === 'error' && (
                <span className="text-intervention text-sm">✗</span>
              )}
              {node.status === 'running' && (
                <div className="w-4 h-4 border-2 border-neuro border-t-transparent rounded-full animate-spin" />
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Workflow-Legende */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-symbolic" />
            <span className="text-gray-400">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-neuro animate-pulse" />
            <span className="text-gray-400">Running</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-600" />
            <span className="text-gray-400">Pending</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-intervention" />
            <span className="text-gray-400">Error</span>
          </div>
        </div>
      </div>
      
      {/* Performance-Metriken */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Performance Metrics</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-400 mb-1">Total Duration</div>
            <div className="text-lg font-mono text-white">
              {nodes
                .filter(n => n.duration)
                .reduce((sum, n) => sum + (n.duration || 0), 0)
                .toLocaleString()}ms
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400 mb-1">Completed Nodes</div>
            <div className="text-lg font-mono text-white">
              {nodes.filter(n => n.status === 'completed').length} / {nodes.length}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}





