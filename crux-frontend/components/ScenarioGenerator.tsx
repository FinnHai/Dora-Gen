'use client';

import { useState } from 'react';
import { cruxAPI } from '@/lib/api';
import { useCruxStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const SCENARIO_TYPES = [
  {
    value: 'ransomware_double_extortion',
    label: 'Ransomware Double Extortion',
    description: 'Ransomware-Angriff mit doppelter Erpressung (Verschlüsselung + Datenleck)',
  },
  {
    value: 'ddos_critical_functions',
    label: 'DDoS Critical Functions',
    description: 'DDoS-Angriff auf kritische Geschäftsfunktionen',
  },
  {
    value: 'supply_chain_compromise',
    label: 'Supply Chain Compromise',
    description: 'Kompromittierung über Lieferkette',
  },
  {
    value: 'insider_threat_data_manipulation',
    label: 'Insider Threat',
    description: 'Insider-Bedrohung mit Datenmanipulation',
  },
];

interface ScenarioGeneratorProps {
  onGenerate?: (scenarioId: string, injects: any[]) => void;
}

export default function ScenarioGenerator({ onGenerate }: ScenarioGeneratorProps) {
  const [open, setOpen] = useState(false);
  const [scenarioType, setScenarioType] = useState<string>('');
  const [numInjects, setNumInjects] = useState<number>(10);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { setInjects, setCurrentScenarioId, setGraphData, setCriticLogs } = useCruxStore();

  const handleGenerate = async () => {
    if (!scenarioType) {
      setError('Bitte wähle einen Szenario-Typ');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      console.log(`Generating scenario: ${scenarioType} with ${numInjects} injects...`);
      
      const result = await cruxAPI.generateScenario(scenarioType, numInjects);
      
      console.log(`Scenario generated: ${result.scenario_id} with ${result.injects.length} injects`);
      
      // Update store
      setCurrentScenarioId(result.scenario_id);
      setInjects(result.injects);
      
      // Reload graph data
      const [nodes, links] = await Promise.all([
        cruxAPI.fetchGraphNodes(),
        cruxAPI.fetchGraphLinks(),
      ]);
      if (nodes.length > 0 || links.length > 0) {
        setGraphData(nodes, links);
      }
      
      // Load logs
      const logs = await cruxAPI.fetchScenarioLogs(result.scenario_id);
      if (logs.length > 0) {
        setCriticLogs(logs);
      }
      
      // Callback
      if (onGenerate) {
        onGenerate(result.scenario_id, result.injects);
      }
      
      // Close dialog
      setOpen(false);
    } catch (err: any) {
      console.error('Error generating scenario:', err);
      // Extract error message - could be nested
      let errorMessage = 'Fehler beim Generieren des Szenarios';
      if (err.message) {
        errorMessage = err.message;
        // If it's a long error with traceback, show only first line
        if (errorMessage.includes('\n')) {
          errorMessage = errorMessage.split('\n')[0];
        }
      }
      setError(errorMessage);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-neuro hover:bg-neuro/80 text-white font-semibold px-4 py-2 rounded-md transition-all text-sm">
          Neues Szenario
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-panel border-[#30363D] text-[#E6EDF3] max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-[#E6EDF3]">
            Neues Szenario generieren
          </DialogTitle>
          <DialogDescription className="text-sm text-[#8B949E]">
            Erstelle ein neues Krisenszenario mit mehreren Injects
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 mt-4">
          {/* Scenario Type Selection */}
          <div className="space-y-2">
            <Label htmlFor="scenario-type" className="text-sm font-semibold text-[#E6EDF3]">
              Szenario-Typ *
            </Label>
            <Select value={scenarioType} onValueChange={setScenarioType}>
              <SelectTrigger 
                id="scenario-type"
                className="bg-void border-[#30363D] text-[#E6EDF3] h-9"
              >
                <SelectValue placeholder="Wähle einen Szenario-Typ" />
              </SelectTrigger>
              <SelectContent className="bg-panel border-[#30363D]">
                {SCENARIO_TYPES.map((type) => (
                  <SelectItem
                    key={type.value}
                    value={type.value}
                    className="text-[#E6EDF3] hover:bg-[#30363D] focus:bg-[#30363D] cursor-pointer"
                  >
                    <div className="py-1">
                      <div className="font-semibold text-sm">{type.label}</div>
                      <div className="text-xs text-[#8B949E] mt-0.5">{type.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Number of Injects */}
          <div className="space-y-2">
            <Label htmlFor="num-injects" className="text-sm font-semibold text-[#E6EDF3]">
              Anzahl Injects
            </Label>
            <Input
              id="num-injects"
              type="number"
              min={1}
              max={20}
              value={numInjects}
              onChange={(e) => setNumInjects(parseInt(e.target.value) || 10)}
              className="bg-void border-[#30363D] text-[#E6EDF3] h-9"
            />
            <p className="text-xs text-[#8B949E]">
              Empfohlen: 5-15 Injects für ein realistisches Szenario
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-intervention/10 border border-intervention rounded-md">
              <p className="text-sm text-intervention">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <Button
              onClick={handleGenerate}
              disabled={generating || !scenarioType}
              className="flex-1 bg-neuro hover:bg-neuro/80 text-white font-semibold h-9"
            >
              {generating ? (
                <>
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Generiere...
                </>
              ) : (
                'Generieren'
              )}
            </Button>
            <Button
              onClick={() => setOpen(false)}
              disabled={generating}
              variant="outline"
              className="border-[#30363D] text-[#8B949E] hover:bg-[#30363D] hover:text-[#E6EDF3] h-9"
            >
              Abbrechen
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

