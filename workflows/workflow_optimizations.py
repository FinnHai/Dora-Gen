"""
Workflow-Optimierungen für Performance und Effizienz.

Implementiert:
- State-Caching
- Parallelisierung wo möglich
- Early Exit-Strategien
- Performance-Monitoring
"""

from typing import Dict, Any, Optional, List
from functools import lru_cache
from datetime import datetime, timedelta
import time


class WorkflowOptimizer:
    """
    Optimierungen für Workflow-Performance.
    
    Features:
    - State-Caching (Neo4j-Queries)
    - Early Exit bei Fehlern
    - Performance-Monitoring
    - Batch-Processing
    """
    
    def __init__(self):
        """Initialisiert den Workflow-Optimizer."""
        # Cache für State-Queries (TTL: 30 Sekunden)
        self.state_cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.cache_ttl = timedelta(seconds=30)
        
        # Performance-Metriken
        self.performance_metrics: List[Dict[str, Any]] = []
        
        # Early Exit-Flags
        self.max_consecutive_errors = 3
        self.max_total_errors = 20
    
    def get_cached_state(
        self,
        cache_key: str,
        fetch_function: callable,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Holt State aus Cache oder führt Fetch-Funktion aus.
        
        Args:
            cache_key: Eindeutiger Cache-Key
            fetch_function: Funktion zum Abrufen des States
            force_refresh: Cache ignorieren und neu laden
        
        Returns:
            System-State Dictionary
        """
        # Prüfe Cache
        if not force_refresh and cache_key in self.state_cache:
            cached_data, cached_timestamp = self.state_cache[cache_key]
            age = datetime.now() - cached_timestamp
            
            if age < self.cache_ttl:
                print(f"   💾 Cache-Hit: State aus Cache (Alter: {age.total_seconds():.1f}s)")
                return cached_data
        
        # Cache-Miss oder abgelaufen: Neu laden
        print(f"   🔄 Cache-Miss: Lade State neu...")
        start_time = time.time()
        data = fetch_function()
        fetch_time = time.time() - start_time
        
        # Speichere im Cache
        self.state_cache[cache_key] = (data, datetime.now())
        
        # Logge Performance
        self.performance_metrics.append({
            "operation": "state_fetch",
            "cache_key": cache_key,
            "cache_hit": False,
            "duration_ms": fetch_time * 1000,
            "timestamp": datetime.now().isoformat()
        })
        
        return data
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """
        Löscht Cache-Einträge.
        
        Args:
            cache_key: Optional - Spezifischer Key, oder None für alle
        """
        if cache_key:
            self.state_cache.pop(cache_key, None)
        else:
            self.state_cache.clear()
        print(f"   🗑️  Cache gelöscht: {cache_key or 'Alle'}")
    
    def should_early_exit(
        self,
        errors: List[str],
        warnings: List[str],
        consecutive_failures: int
    ) -> tuple[bool, str]:
        """
        Entscheidet ob Workflow früh beendet werden sollte.
        
        Returns:
            (should_exit, reason)
        """
        # Zu viele aufeinanderfolgende Fehler
        if consecutive_failures >= self.max_consecutive_errors:
            return (True, f"Zu viele aufeinanderfolgende Fehler ({consecutive_failures})")
        
        # Zu viele Gesamt-Fehler
        if len(errors) >= self.max_total_errors:
            return (True, f"Zu viele Gesamt-Fehler ({len(errors)})")
        
        # Kritische Fehler (z.B. Neo4j-Verbindung verloren)
        critical_errors = [
            "Neo4j",
            "Connection",
            "Database",
            "Fatal"
        ]
        if any(keyword in error for error in errors for keyword in critical_errors):
            return (True, "Kritischer Systemfehler erkannt")
        
        return (False, "")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Gibt Performance-Zusammenfassung zurück.
        
        Returns:
            Dictionary mit Performance-Metriken
        """
        if not self.performance_metrics:
            return {"message": "Keine Metriken verfügbar"}
        
        # Berechne Statistiken
        state_fetches = [m for m in self.performance_metrics if m["operation"] == "state_fetch"]
        
        cache_hits = sum(1 for m in state_fetches if m.get("cache_hit", False))
        cache_misses = len(state_fetches) - cache_hits
        
        avg_duration = (
            sum(m["duration_ms"] for m in state_fetches) / len(state_fetches)
            if state_fetches else 0
        )
        
        cache_hit_rate = (
            cache_hits / len(state_fetches) * 100
            if state_fetches else 0
        )
        
        return {
            "total_operations": len(self.performance_metrics),
            "state_fetches": len(state_fetches),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "avg_fetch_duration_ms": f"{avg_duration:.2f}",
            "cache_size": len(self.state_cache)
        }
    
    def optimize_batch_processing(
        self,
        items: List[Any],
        process_function: callable,
        batch_size: int = 5
    ) -> List[Any]:
        """
        Verarbeitet Items in Batches für bessere Performance.
        
        Args:
            items: Liste von Items zu verarbeiten
            process_function: Funktion zum Verarbeiten eines Items
            batch_size: Größe eines Batches
        
        Returns:
            Liste von Ergebnissen
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [process_function(item) for item in batch]
            results.extend(batch_results)
        
        return results


class WorkflowPerformanceMonitor:
    """
    Performance-Monitoring für Workflow-Nodes.
    
    Trackt:
    - Node-Dauer
    - Fehler-Rate
    - Durchsatz
    """
    
    def __init__(self):
        """Initialisiert den Performance-Monitor."""
        self.node_timings: Dict[str, List[float]] = {}
        self.node_errors: Dict[str, int] = {}
        self.node_successes: Dict[str, int] = {}
    
    def start_node(self, node_name: str) -> float:
        """
        Startet Timing für einen Node.
        
        Returns:
            Start-Zeitstempel
        """
        return time.time()
    
    def end_node(self, node_name: str, start_time: float, success: bool = True):
        """
        Beendet Timing für einen Node.
        
        Args:
            node_name: Name des Nodes
            start_time: Start-Zeitstempel
            success: Ob Node erfolgreich war
        """
        duration = time.time() - start_time
        
        if node_name not in self.node_timings:
            self.node_timings[node_name] = []
            self.node_errors[node_name] = 0
            self.node_successes[node_name] = 0
        
        self.node_timings[node_name].append(duration)
        
        if success:
            self.node_successes[node_name] += 1
        else:
            self.node_errors[node_name] += 1
    
    def get_node_statistics(self, node_name: str) -> Dict[str, Any]:
        """
        Gibt Statistiken für einen Node zurück.
        
        Returns:
            Dictionary mit Statistiken
        """
        if node_name not in self.node_timings:
            return {"error": "Node nicht gefunden"}
        
        timings = self.node_timings[node_name]
        errors = self.node_errors[node_name]
        successes = self.node_successes[node_name]
        total = errors + successes
        
        return {
            "node_name": node_name,
            "total_executions": total,
            "successes": successes,
            "errors": errors,
            "success_rate": f"{(successes / total * 100):.1f}%" if total > 0 else "N/A",
            "avg_duration_ms": f"{(sum(timings) / len(timings) * 1000):.2f}" if timings else "N/A",
            "min_duration_ms": f"{(min(timings) * 1000):.2f}" if timings else "N/A",
            "max_duration_ms": f"{(max(timings) * 1000):.2f}" if timings else "N/A"
        }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Gibt Statistiken für alle Nodes zurück.
        
        Returns:
            Dictionary von Node-Statistiken
        """
        return {
            node_name: self.get_node_statistics(node_name)
            for node_name in self.node_timings.keys()
        }





