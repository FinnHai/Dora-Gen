"""
Advanced Scientific Frontend für Forensic-Datenanalyse
Analysen 1-10: Temporale Dynamik & Prozess-Mining
Analysen 11-20: Semantische Forensik & NLP
Analysen 21-30: Agenten-Performance & Qualitäts-Metriken
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Statistical tests
try:
    import scipy.stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    scipy_stats = None

# NLP libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Streamlit Configuration
st.set_page_config(
    page_title="Forensic Analysis - DORA Scenario Generator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Scientific CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3, h4 {
        color: #1e293b;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stMarkdown, .stText, p, div, span {
        color: #1e293b;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: white;
    }
    
    .analysis-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .insight-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 6px;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialisiert Session State Variablen."""
    defaults = {
        "forensic_data": None,
        "loaded_data": False,
        "analysis_cache": {}
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def load_forensic_jsonl(file_path: str) -> pd.DataFrame:
    """Lädt Forensic JSONL-Datei und konvertiert zu DataFrame."""
    try:
        events = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    continue
        
        if not events:
            return pd.DataFrame()
        
        # Konvertiere zu DataFrame mit Flattening
        df = pd.json_normalize(events)
        
        # Normalisiere Timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.sort_values('timestamp').reset_index(drop=True)
            df['timestamp_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
        
        # Extrahiere wichtige Felder
        if 'data.validation.is_valid' in df.columns:
            df['is_valid'] = df['data.validation.is_valid']
        if 'data.validation.logical_consistency' in df.columns:
            df['logical_consistency'] = df['data.validation.logical_consistency']
        if 'data.validation.dora_compliance' in df.columns:
            df['dora_compliance'] = df['data.validation.dora_compliance']
        if 'data.validation.causal_validity' in df.columns:
            df['causal_validity'] = df['data.validation.causal_validity']
        if 'data.validation.errors' in df.columns:
            df['errors'] = df['data.validation.errors']
            df['error_count'] = df['errors'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            df['errors_text'] = df['errors'].apply(lambda x: ' '.join(str(e) for e in x) if isinstance(x, list) else str(x))
        if 'data.validation.warnings' in df.columns:
            df['warnings'] = df['data.validation.warnings']
            df['warning_count'] = df['warnings'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            df['warnings_text'] = df['warnings'].apply(lambda x: ' '.join(str(w) for w in x) if isinstance(x, list) else str(x))
        if 'data.decision' in df.columns:
            df['decision'] = df['data.decision']
        if 'data.inject_id' in df.columns:
            df['inject_id'] = df['data.inject_id']
        
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Forensic-Daten: {e}")
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()


# ============================================================================
# ANALYSE 1: REFINEMENT VELOCITY
# ============================================================================

def analyze_refinement_velocity(df: pd.DataFrame) -> Dict[str, Any]:
    """1. Refinement Velocity: Durchschnittliche Zeitdauer zwischen Iteration n und n+1."""
    if 'timestamp' not in df.columns or 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    velocities = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) < 2:
            continue
        
        for i in range(1, len(inject_df)):
            prev_row = inject_df.iloc[i-1]
            curr_row = inject_df.iloc[i]
            
            time_diff = (curr_row['timestamp'] - prev_row['timestamp']).total_seconds()
            refine_diff = curr_row['refine_count'] - prev_row['refine_count']
            
            if refine_diff >= 0:  # Nur wenn Refine-Count steigt oder gleich bleibt
                velocities.append({
                    'inject_id': inject_id,
                    'from_refine': prev_row['refine_count'],
                    'to_refine': curr_row['refine_count'],
                    'time_diff_seconds': time_diff,
                    'scenario_id': curr_row.get('scenario_id', 'unknown')
                })
    
    if not velocities:
        return {}
    
    vel_df = pd.DataFrame(velocities)
    
    return {
        'mean_velocity': vel_df['time_diff_seconds'].mean(),
        'median_velocity': vel_df['time_diff_seconds'].median(),
        'std_velocity': vel_df['time_diff_seconds'].std(),
        'min_velocity': vel_df['time_diff_seconds'].min(),
        'max_velocity': vel_df['time_diff_seconds'].max(),
        'data': vel_df,
        'by_refine': vel_df.groupby('from_refine')['time_diff_seconds'].agg(['mean', 'count']).to_dict('index')
    }


# ============================================================================
# ANALYSE 2: SCENARIO FATIGUE ANALYSIS
# ============================================================================

def analyze_scenario_fatigue(df: pd.DataFrame) -> Dict[str, Any]:
    """2. Scenario Fatigue: Korrelation zwischen Fortschritt (iteration) und refine_count."""
    if 'iteration' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    # Gruppiere nach Szenario und Iteration
    fatigue_data = []
    
    for scenario_id in df['scenario_id'].unique():
        scenario_df = df[df['scenario_id'] == scenario_id].sort_values('iteration')
        
        for iteration in scenario_df['iteration'].unique():
            iter_df = scenario_df[scenario_df['iteration'] == iteration]
            max_refines = iter_df['refine_count'].max()
            mean_refines = iter_df['refine_count'].mean()
            has_error = (iter_df['error_count'] > 0).any()
            
            fatigue_data.append({
                'scenario_id': scenario_id,
                'iteration': iteration,
                'max_refines': max_refines,
                'mean_refines': mean_refines,
                'has_error': has_error,
                'inject_id': iter_df.iloc[0]['inject_id'] if len(iter_df) > 0 else None
            })
    
    if not fatigue_data:
        return {}
    
    fatigue_df = pd.DataFrame(fatigue_data)
    
    # Berechne Korrelation pro Szenario
    correlations = {}
    for scenario_id in fatigue_df['scenario_id'].unique():
        scenario_data = fatigue_df[fatigue_df['scenario_id'] == scenario_id].sort_values('iteration')
        if len(scenario_data) > 1:
            corr = scenario_data['iteration'].corr(scenario_data['max_refines'])
            correlations[scenario_id] = corr
    
    overall_corr = fatigue_df['iteration'].corr(fatigue_df['max_refines']) if len(fatigue_df) > 1 else 0
    
    return {
        'overall_correlation': overall_corr,
        'per_scenario_correlation': correlations,
        'fatigue_detected': overall_corr > 0.2,  # Positive Korrelation = mehr Fehler später
        'data': fatigue_df
    }


# ============================================================================
# ANALYSE 3: BURSTINESS OF ERRORS
# ============================================================================

def analyze_burstiness(df: pd.DataFrame) -> Dict[str, Any]:
    """3. Burstiness: Treten Fehler in Clustern auf oder gleichverteilt?"""
    if 'timestamp' not in df.columns or 'is_valid' not in df.columns:
        return {}
    
    df_sorted = df.sort_values('timestamp')
    
    # Identifiziere Fehler-Events
    error_events = df_sorted[~df_sorted['is_valid']].copy()
    
    if len(error_events) < 2:
        return {}
    
    # Berechne Zeitintervalle zwischen Fehlern
    intervals = []
    for i in range(1, len(error_events)):
        time_diff = (error_events.iloc[i]['timestamp'] - error_events.iloc[i-1]['timestamp']).total_seconds()
        intervals.append(time_diff)
    
    if not intervals:
        return {}
    
    intervals = np.array(intervals)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)
    
    # Burstiness-Index nach Goh & Barabási
    if (std_interval + mean_interval) > 0:
        burstiness = (std_interval - mean_interval) / (std_interval + mean_interval)
    else:
        burstiness = 0
    
    # Memory-Koeffizient (Autokorrelation)
    memory = 0
    if len(intervals) > 1 and std_interval > 0:
        memory = np.corrcoef(intervals[:-1], intervals[1:])[0, 1] if len(intervals) > 1 else 0
    
    return {
        'burstiness_index': burstiness,
        'memory_coefficient': memory,
        'mean_interval': mean_interval,
        'std_interval': std_interval,
        'is_bursty': burstiness > 0.5,
        'has_memory': abs(memory) > 0.3,
        'intervals': intervals.tolist()
    }


# ============================================================================
# ANALYSE 4: CONVERGENCE RATE
# ============================================================================

def analyze_convergence_rate(df: pd.DataFrame) -> Dict[str, Any]:
    """4. Convergence Rate: Wie schnell konvergiert ein Inject gegen is_valid=True?"""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns or 'is_valid' not in df.columns:
        return {}
    
    convergence_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) == 0:
            continue
        
        # Finde ersten erfolgreichen Versuch
        valid_rows = inject_df[inject_df['is_valid'] == True]
        
        if len(valid_rows) > 0:
            first_valid_refine = valid_rows.iloc[0]['refine_count']
            first_valid_time = valid_rows.iloc[0]['timestamp']
            first_draft_time = inject_df.iloc[0]['timestamp']
            time_to_valid = (first_valid_time - first_draft_time).total_seconds()
            
            convergence_data.append({
                'inject_id': inject_id,
                'refines_to_valid': first_valid_refine,
                'time_to_valid_seconds': time_to_valid,
                'converged': True,
                'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
            })
        else:
            # Nie erfolgreich
            convergence_data.append({
                'inject_id': inject_id,
                'refines_to_valid': inject_df['refine_count'].max(),
                'time_to_valid_seconds': None,
                'converged': False,
                'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
            })
    
    if not convergence_data:
        return {}
    
    conv_df = pd.DataFrame(convergence_data)
    converged_df = conv_df[conv_df['converged'] == True]
    
    return {
        'mean_refines_to_valid': converged_df['refines_to_valid'].mean() if len(converged_df) > 0 else 0,
        'median_refines_to_valid': converged_df['refines_to_valid'].median() if len(converged_df) > 0 else 0,
        'convergence_rate': (len(converged_df) / len(conv_df) * 100) if len(conv_df) > 0 else 0,
        'mean_time_to_valid': converged_df['time_to_valid_seconds'].mean() if len(converged_df) > 0 else 0,
        'data': conv_df
    }


# ============================================================================
# ANALYSE 5: LAG-AUTOKORRELATION
# ============================================================================

def analyze_lag_autocorrelation(df: pd.DataFrame) -> Dict[str, Any]:
    """5. Lag-Autokorrelation: Beeinflusst ein schwieriger Inject den nächsten?"""
    if 'scenario_id' not in df.columns or 'iteration' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    autocorr_data = []
    
    for scenario_id in df['scenario_id'].unique():
        scenario_df = df[df['scenario_id'] == scenario_id].sort_values('iteration')
        
        # Gruppiere nach Iteration, nimm max Refine-Count pro Iteration
        iteration_refines = scenario_df.groupby('iteration')['refine_count'].max().reset_index()
        iteration_refines = iteration_refines.sort_values('iteration')
        
        if len(iteration_refines) < 2:
            continue
        
        # Erstelle Paare: (refine_count[i], refine_count[i+1])
        for i in range(len(iteration_refines) - 1):
            autocorr_data.append({
                'scenario_id': scenario_id,
                'current_refines': iteration_refines.iloc[i]['refine_count'],
                'next_refines': iteration_refines.iloc[i+1]['refine_count'],
                'current_iteration': iteration_refines.iloc[i]['iteration']
            })
    
    if not autocorr_data:
        return {}
    
    autocorr_df = pd.DataFrame(autocorr_data)
    
    # Berechne Korrelation
    if len(autocorr_df) > 1:
        correlation = autocorr_df['current_refines'].corr(autocorr_df['next_refines'])
    else:
        correlation = 0
    
    return {
        'lag1_autocorrelation': correlation,
        'has_cascade_effect': correlation > 0.3,  # Positive Korrelation = Kaskadeneffekt
        'data': autocorr_df
    }


# ============================================================================
# ANALYSE 6: TIME-TO-ACCEPTANCE (TTA)
# ============================================================================

def analyze_time_to_acceptance(df: pd.DataFrame) -> Dict[str, Any]:
    """6. Time-to-Acceptance: Gesamtzeit vom ersten Draft bis zum finalen accept."""
    if 'timestamp' not in df.columns or 'inject_id' not in df.columns or 'decision' not in df.columns:
        return {}
    
    tta_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values('timestamp')
        
        if len(inject_df) == 0:
            continue
        
        first_timestamp = inject_df.iloc[0]['timestamp']
        
        # Finde letztes Accept
        accepted_df = inject_df[inject_df['decision'] == 'accept']
        
        if len(accepted_df) > 0:
            last_accept = accepted_df.iloc[-1]['timestamp']
            tta = (last_accept - first_timestamp).total_seconds()
            
            tta_data.append({
                'inject_id': inject_id,
                'tta_seconds': tta,
                'tta_minutes': tta / 60,
                'refines': inject_df['refine_count'].max(),
                'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
            })
    
    if not tta_data:
        return {}
    
    tta_df = pd.DataFrame(tta_data)
    
    return {
        'mean_tta_seconds': tta_df['tta_seconds'].mean(),
        'median_tta_seconds': tta_df['tta_seconds'].median(),
        'mean_tta_minutes': tta_df['tta_minutes'].mean(),
        'std_tta_seconds': tta_df['tta_seconds'].std(),
        'min_tta': tta_df['tta_seconds'].min(),
        'max_tta': tta_df['tta_seconds'].max(),
        'data': tta_df
    }


# ============================================================================
# ANALYSE 7: OSCILLATION DETECTION
# ============================================================================

def detect_oscillations(df: pd.DataFrame) -> Dict[str, Any]:
    """7. Oscillation Detection: Injects, die zwischen Fehlerzuständen pendeln."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    oscillations = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) < 3:
            continue
        
        # Kategorisiere Fehlertypen
        error_types = []
        for idx, row in inject_df.iterrows():
            error_type = 'none'
            if row.get('error_count', 0) > 0:
                errors = row.get('errors', [])
                if isinstance(errors, list) and len(errors) > 0:
                    error_text = ' '.join(str(e) for e in errors).lower()
                    if 'logical' in error_text or 'consistency' in error_text:
                        error_type = 'logical'
                    elif 'causal' in error_text:
                        error_type = 'causal'
                    elif 'dora' in error_text or 'regulatory' in error_text:
                        error_type = 'dora'
                    else:
                        error_type = 'other'
            error_types.append(error_type)
        
        # Prüfe auf Oszillation (Wechsel zwischen verschiedenen Fehlertypen)
        unique_types = [t for t in error_types if t != 'none']
        if len(set(unique_types)) > 1:  # Mehrere verschiedene Fehlertypen
            # Zähle Wechsel
            switches = 0
            for i in range(1, len(error_types)):
                if error_types[i] != error_types[i-1] and error_types[i] != 'none' and error_types[i-1] != 'none':
                    switches += 1
            
            if switches >= 2:  # Mindestens 2 Wechsel = Oszillation
                oscillations.append({
                    'inject_id': inject_id,
                    'oscillation_count': switches,
                    'error_types': list(set(unique_types)),
                    'refines': inject_df['refine_count'].max(),
                    'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
                })
    
    if not oscillations:
        return {'oscillations': [], 'count': 0}
    
    osc_df = pd.DataFrame(oscillations)
    
    return {
        'oscillations': oscillations,
        'count': len(oscillations),
        'mean_switches': osc_df['oscillation_count'].mean(),
        'data': osc_df
    }


# ============================================================================
# ANALYSE 8: VALIDATION BOTTLENECK IDENTIFICATION
# ============================================================================

def identify_validation_bottlenecks(df: pd.DataFrame) -> Dict[str, Any]:
    """8. Validation Bottleneck: Welcher Validierungsschritt verzögert am meisten?"""
    if 'refine_count' not in df.columns:
        return {}
    
    bottleneck_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) < 2:
            continue
        
        # Analysiere welche Validierungsschritte fehlschlagen
        for i in range(len(inject_df)):
            row = inject_df.iloc[i]
            
            if not row.get('is_valid', True):
                # Welche Validierungsschritte sind falsch?
                failed_checks = []
                if not row.get('logical_consistency', True):
                    failed_checks.append('logical')
                if not row.get('causal_validity', True):
                    failed_checks.append('causal')
                if not row.get('dora_compliance', True):
                    failed_checks.append('dora')
                
                bottleneck_data.append({
                    'inject_id': inject_id,
                    'refine_count': row['refine_count'],
                    'failed_checks': failed_checks,
                    'all_failed': ','.join(failed_checks) if failed_checks else 'unknown'
                })
    
    if not bottleneck_data:
        return {}
    
    bottleneck_df = pd.DataFrame(bottleneck_data)
    
    # Zähle Häufigkeit jedes Bottlenecks
    bottleneck_counts = Counter(bottleneck_df['all_failed'])
    
    # Analysiere einzelne Checks
    logical_fails = len(bottleneck_df[bottleneck_df['all_failed'].str.contains('logical', na=False)])
    causal_fails = len(bottleneck_df[bottleneck_df['all_failed'].str.contains('causal', na=False)])
    dora_fails = len(bottleneck_df[bottleneck_df['all_failed'].str.contains('dora', na=False)])
    
    total_fails = len(bottleneck_df)
    
    return {
        'bottleneck_frequency': dict(bottleneck_counts),
        'logical_failure_rate': (logical_fails / total_fails * 100) if total_fails > 0 else 0,
        'causal_failure_rate': (causal_fails / total_fails * 100) if total_fails > 0 else 0,
        'dora_failure_rate': (dora_fails / total_fails * 100) if total_fails > 0 else 0,
        'main_bottleneck': max(['logical', 'causal', 'dora'], 
                              key=lambda x: {'logical': logical_fails, 'causal': causal_fails, 'dora': dora_fails}.get(x, 0)),
        'data': bottleneck_df
    }


# ============================================================================
# ANALYSE 9: CHANGE POINT DETECTION
# ============================================================================

def detect_change_points(df: pd.DataFrame) -> Dict[str, Any]:
    """9. Change Point Detection: Zeitpunkte, an denen sich Qualität signifikant ändert."""
    if 'timestamp' not in df.columns or 'is_valid' not in df.columns:
        return {}
    
    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    
    # Verwende Sliding Window für Change Point Detection
    window_size = min(10, len(df_sorted) // 4)
    if window_size < 3:
        return {}
    
    change_points = []
    
    # Berechne Erfolgsrate in Sliding Windows
    for i in range(window_size, len(df_sorted) - window_size):
        window_before = df_sorted.iloc[i-window_size:i]
        window_after = df_sorted.iloc[i:i+window_size]
        
        success_rate_before = window_before['is_valid'].mean()
        success_rate_after = window_after['is_valid'].mean()
        
        # Signifikanztest (einfacher t-Test)
        if SCIPY_AVAILABLE and len(window_before) > 1 and len(window_after) > 1:
            try:
                t_stat, p_value = scipy_stats.ttest_ind(
                    window_before['is_valid'].astype(float),
                    window_after['is_valid'].astype(float)
                )
                
                if p_value < 0.05 and abs(success_rate_after - success_rate_before) > 0.2:
                    change_points.append({
                        'timestamp': df_sorted.iloc[i]['timestamp'],
                        'index': i,
                        'p_value': p_value,
                        'success_rate_before': success_rate_before,
                        'success_rate_after': success_rate_after,
                        'change_direction': 'improvement' if success_rate_after > success_rate_before else 'degradation'
                    })
            except:
                pass
    
    return {
        'change_points': change_points,
        'count': len(change_points),
        'data': pd.DataFrame(change_points) if change_points else pd.DataFrame()
    }


# ============================================================================
# ANALYSE 10: REFINEMENT LOOPS TRAJECTORY
# ============================================================================

def analyze_refinement_trajectories(df: pd.DataFrame) -> Dict[str, Any]:
    """10. Refinement Loops Trajectory: Visualisierung der Schleifen als Zustandsraum."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns or 'is_valid' not in df.columns:
        return {}
    
    trajectories = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) == 0:
            continue
        
        trajectory = []
        for idx, row in inject_df.iterrows():
            # Zustand: (refine_count, is_valid, error_count)
            state = {
                'refine_count': row['refine_count'],
                'is_valid': row.get('is_valid', False),
                'error_count': row.get('error_count', 0),
                'timestamp': row.get('timestamp')
            }
            trajectory.append(state)
        
        trajectories.append({
            'inject_id': inject_id,
            'trajectory': trajectory,
            'max_refines': inject_df['refine_count'].max(),
            'final_valid': inject_df.iloc[-1].get('is_valid', False),
            'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
        })
    
    return {
        'trajectories': trajectories,
        'count': len(trajectories),
        'avg_max_refines': np.mean([t['max_refines'] for t in trajectories]) if trajectories else 0
    }


# ============================================================================
# ANALYSE 11-20: SEMANTISCHE FORENSIK & NLP
# ============================================================================

def analyze_error_topics(df: pd.DataFrame, n_topics: int = 5) -> Dict[str, Any]:
    """11. Error Topic Modeling: Automatische Clusterung der Fehlermeldungen."""
    if not SKLEARN_AVAILABLE or 'errors_text' not in df.columns:
        return {}
    
    error_texts = df[df['errors_text'].notna() & (df['errors_text'] != '')]['errors_text'].tolist()
    
    if len(error_texts) < n_topics:
        return {'error': f'Nicht genug Fehlertexte ({len(error_texts)} < {n_topics})'}
    
    try:
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            min_df=2,
            max_df=0.95
        )
        X = vectorizer.fit_transform(error_texts)
        
        # LDA Topic Modeling
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=10
        )
        lda.fit(X)
        
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            top_weights = [topic[i] for i in top_words_idx]
            
            topics.append({
                'topic_id': topic_idx,
                'top_words': top_words,
                'top_weights': top_weights,
                'topic_weight': topic.sum()
            })
        
        # Dokument-Topic-Zuordnung
        doc_topic_dist = lda.transform(X)
        dominant_topics = doc_topic_dist.argmax(axis=1)
        
        return {
            'topics': topics,
            'n_documents': len(error_texts),
            'dominant_topics': dominant_topics.tolist(),
            'topic_distribution': Counter(dominant_topics)
        }
    except Exception as e:
        return {'error': str(e)}


def extract_hallucination_entities(df: pd.DataFrame) -> Dict[str, Any]:
    """12. Hallucination Entity Extraction: Extrahieren aller Asset-Namen aus Warnungen."""
    if 'warnings_text' not in df.columns:
        return {}
    
    # Patterns für Asset-IDs und "unknown asset" Meldungen
    asset_patterns = [
        r'SRV-[A-Z0-9-]+',
        r'APP-[A-Z0-9-]+',
        r'DB-[A-Z0-9-]+',
        r'SVC-[A-Z0-9-]+',
        r'SYS-[A-Z0-9-]+',
        r'BACKUP-[A-Z0-9-]+',
        r'EMAIL-[A-Z0-9-]+'
    ]
    
    # Patterns für "unknown" oder "existiert nicht" Meldungen
    unknown_patterns = [
        r'existiert nicht',
        r'nicht verfügbar',
        r'unknown asset',
        r'not found',
        r'does not exist'
    ]
    
    hallucinated_assets = set()
    unknown_mentions = []
    
    for idx, row in df.iterrows():
        warning_text = str(row.get('warnings_text', '')).lower()
        error_text = str(row.get('errors_text', '')).lower()
        combined_text = warning_text + ' ' + error_text
        
        # Prüfe auf "unknown" Meldungen
        is_unknown = any(re.search(pattern, combined_text, re.IGNORECASE) for pattern in unknown_patterns)
        
        if is_unknown:
            # Extrahiere Asset-IDs aus diesem Text
            for pattern in asset_patterns:
                matches = re.findall(pattern, combined_text, re.IGNORECASE)
                hallucinated_assets.update(matches)
            
            unknown_mentions.append({
                'inject_id': row.get('inject_id', 'unknown'),
                'text': combined_text[:200]  # Erste 200 Zeichen
            })
    
    return {
        'hallucinated_assets': sorted(list(hallucinated_assets)),
        'count': len(hallucinated_assets),
        'unknown_mentions': unknown_mentions[:20],  # Erste 20
        'total_unknown_mentions': len(unknown_mentions)
    }


def analyze_warning_sentiment(df: pd.DataFrame) -> Dict[str, Any]:
    """13. Sentiment Analysis der Warnungen: Wird der Ton schärfer bei wiederholten Fehlern?"""
    if 'warnings_text' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    # Einfache Sentiment-Indikatoren (ohne externe Library)
    negative_words = [
        'fehler', 'error', 'problem', 'warnung', 'warning', 'inkonsistent', 'inconsistent',
        'widerspruch', 'contradiction', 'nicht erfüllt', 'not met', 'fehlgeschlagen', 'failed',
        'kritisch', 'critical', 'gefahr', 'danger', 'problematisch', 'problematic'
    ]
    
    sentiment_data = []
    
    for idx, row in df.iterrows():
        warning_text = str(row.get('warnings_text', '')).lower()
        refine_count = row.get('refine_count', 0)
        
        if warning_text:
            # Zähle negative Wörter
            negative_count = sum(1 for word in negative_words if word in warning_text)
            text_length = len(warning_text.split())
            sentiment_score = (negative_count / text_length * 100) if text_length > 0 else 0
            
            sentiment_data.append({
                'refine_count': refine_count,
                'sentiment_score': sentiment_score,
                'negative_words': negative_count,
                'text_length': text_length
            })
    
    if not sentiment_data:
        return {}
    
    sentiment_df = pd.DataFrame(sentiment_data)
    
    # Korrelation zwischen Refine-Count und Sentiment
    if len(sentiment_df) > 1:
        correlation = sentiment_df['refine_count'].corr(sentiment_df['sentiment_score'])
    else:
        correlation = 0
    
    return {
        'mean_sentiment_by_refine': sentiment_df.groupby('refine_count')['sentiment_score'].mean().to_dict(),
        'correlation_refine_sentiment': correlation,
        'gets_sharper': correlation > 0.2,
        'data': sentiment_df
    }


def calculate_semantic_similarity(df: pd.DataFrame) -> Dict[str, Any]:
    """14. Semantic Similarity Matrix: Wie ähnlich sind sich Fehlertexte aufeinanderfolgender Injects?"""
    if not SKLEARN_AVAILABLE or 'errors_text' not in df.columns:
        return {}
    
    # Gruppiere nach Inject-ID und sortiere nach Refine-Count
    similarity_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        error_texts = inject_df[inject_df['errors_text'].notna() & (inject_df['errors_text'] != '')]['errors_text'].tolist()
        
        if len(error_texts) < 2:
            continue
        
        try:
            vectorizer = TfidfVectorizer(max_features=50)
            X = vectorizer.fit_transform(error_texts)
            similarity_matrix = cosine_similarity(X)
            
            # Berechne Ähnlichkeit zwischen aufeinanderfolgenden Fehlern
            sequential_similarities = []
            for i in range(len(similarity_matrix) - 1):
                sequential_similarities.append(similarity_matrix[i, i+1])
            
            if sequential_similarities:
                similarity_data.append({
                    'inject_id': inject_id,
                    'mean_sequential_similarity': np.mean(sequential_similarities),
                    'is_repetitive': np.mean(sequential_similarities) > 0.5
                })
        except:
            continue
    
    if not similarity_data:
        return {}
    
    sim_df = pd.DataFrame(similarity_data)
    
    return {
        'mean_similarity': sim_df['mean_sequential_similarity'].mean(),
        'repetitive_injects': sim_df['is_repetitive'].sum(),
        'repetitive_rate': (sim_df['is_repetitive'].sum() / len(sim_df) * 100) if len(sim_df) > 0 else 0,
        'data': sim_df
    }


def extract_mitre_mismatches(df: pd.DataFrame) -> Dict[str, Any]:
    """15. MITRE TTP Mismatch Frequency: Welche Techniken werden falsch verwendet?"""
    if 'errors_text' not in df.columns:
        return {}
    
    mitre_pattern = r'T\d{4,5}'
    mismatches = []
    mismatch_contexts = defaultdict(list)
    
    for idx, row in df.iterrows():
        error_text = str(row.get('errors_text', ''))
        if error_text:
            matches = re.findall(mitre_pattern, error_text, re.IGNORECASE)
            mismatches.extend(matches)
            
            for match in matches:
                # Extrahiere Kontext (Satz um die MITRE-ID)
                sentences = re.split(r'[.!?]', error_text)
                for sentence in sentences:
                    if match in sentence:
                        mismatch_contexts[match].append(sentence.strip()[:150])
                        break
    
    mismatch_counts = Counter(mismatches)
    
    # Analysiere häufigste Mismatches
    top_mismatches = []
    for mitre_id, count in mismatch_counts.most_common(10):
        top_mismatches.append({
            'mitre_id': mitre_id,
            'frequency': count,
            'sample_contexts': mismatch_contexts[mitre_id][:3]
        })
    
    return {
        'mismatch_frequency': dict(mismatch_counts),
        'total_mismatches': len(mismatches),
        'unique_mismatches': len(mismatch_counts),
        'top_mismatches': top_mismatches
    }


def analyze_complexity_error_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """16. Complexity-Error-Correlation: Korrelation zwischen Textlänge und Refinements."""
    if 'errors_text' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    complexity_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values('refine_count')
        
        if len(inject_df) == 0:
            continue
        
        max_refines = inject_df['refine_count'].max()
        
        # Berechne Komplexität aus allen Fehlertexten dieses Injects
        all_errors = inject_df[inject_df['errors_text'].notna()]['errors_text'].tolist()
        total_error_length = sum(len(str(e)) for e in all_errors)
        avg_error_length = total_error_length / len(all_errors) if all_errors else 0
        error_count = len(all_errors)
        
        complexity_data.append({
            'inject_id': inject_id,
            'max_refines': max_refines,
            'total_error_length': total_error_length,
            'avg_error_length': avg_error_length,
            'error_count': error_count,
            'complexity_score': total_error_length * error_count  # Einfacher Komplexitäts-Score
        })
    
    if not complexity_data:
        return {}
    
    comp_df = pd.DataFrame(complexity_data)
    
    # Korrelationen
    correlations = {}
    if len(comp_df) > 1:
        correlations['refines_vs_length'] = comp_df['max_refines'].corr(comp_df['total_error_length'])
        correlations['refines_vs_avg_length'] = comp_df['max_refines'].corr(comp_df['avg_error_length'])
        correlations['refines_vs_complexity'] = comp_df['max_refines'].corr(comp_df['complexity_score'])
    
    return {
        'correlations': correlations,
        'mean_complexity': comp_df['complexity_score'].mean(),
        'data': comp_df
    }


def analyze_dora_gaps(df: pd.DataFrame) -> Dict[str, Any]:
    """17. DORA Gap Analysis: Häufigkeitsanalyse fehlender regulatorischer Keywords."""
    if 'warnings_text' not in df.columns:
        return {}
    
    dora_keywords = {
        'Risk Management Framework': ['risk management', 'risikomanagement', 'risk framework'],
        'Business Continuity Policy': ['business continuity', 'geschäftskontinuität', 'bcp', 'continuity policy'],
        'Response Plan': ['response plan', 'vorfallreaktion', 'incident response plan'],
        'Recovery Plan': ['recovery plan', 'wiederherstellungsplan', 'recovery'],
        'RTO': ['rto', 'recovery time objective', 'wiederherstellungszeit'],
        'RPO': ['rpo', 'recovery point objective', 'wiederherstellungspunkt'],
        'TLPT': ['tlpt', 'time to live production', 'produktionszeit']
    }
    
    gap_analysis = {}
    missing_keywords = defaultdict(int)
    
    for keyword, variants in dora_keywords.items():
        found_count = 0
        missing_count = 0
        
        for idx, row in df.iterrows():
            warning_text = str(row.get('warnings_text', '')).lower()
            error_text = str(row.get('errors_text', '')).lower()
            combined_text = warning_text + ' ' + error_text
            
            # Prüfe ob Keyword fehlt (in "nicht getestet" Kontexten)
            if any(variant in combined_text for variant in variants):
                found_count += 1
            elif 'nicht getestet' in combined_text or 'not tested' in combined_text or 'not met' in combined_text:
                missing_count += 1
                missing_keywords[keyword] += 1
        
        gap_analysis[keyword] = {
            'found': found_count,
            'missing': missing_count,
            'total_mentions': found_count + missing_count
        }
    
    return {
        'gap_analysis': gap_analysis,
        'missing_keywords': dict(missing_keywords),
        'total_gaps': sum(missing_keywords.values())
    }


def build_keyword_cooccurrence_network(df: pd.DataFrame) -> Dict[str, Any]:
    """18. Keyword Co-occurrence Network: Welche Begriffe tauchen oft gemeinsam auf?"""
    if 'errors_text' not in df.columns:
        return {}
    
    # Wichtige Keywords extrahieren
    important_keywords = [
        'asset', 'mitre', 'ttp', 'logical', 'causal', 'dora', 'regulatory',
        'consistency', 'validity', 'compliance', 'temporal', 'phase',
        'srv', 'app', 'compromised', 'degraded', 'offline', 'suspicious'
    ]
    
    cooccurrence = defaultdict(int)
    keyword_docs = defaultdict(set)
    
    for idx, row in df.iterrows():
        error_text = str(row.get('errors_text', '')).lower()
        if not error_text:
            continue
        
        # Finde Keywords im Text
        found_keywords = [kw for kw in important_keywords if kw in error_text]
        
        # Zähle Co-occurrences
        for i, kw1 in enumerate(found_keywords):
            keyword_docs[kw1].add(idx)
            for kw2 in found_keywords[i+1:]:
                pair = tuple(sorted([kw1, kw2]))
                cooccurrence[pair] += 1
    
    # Top Co-occurrences
    top_pairs = sorted(cooccurrence.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        'cooccurrence_pairs': {f"{pair[0]} + {pair[1]}": count for pair, count in top_pairs},
        'keyword_frequency': {kw: len(docs) for kw, docs in keyword_docs.items()},
        'top_pairs': [{'keywords': f"{pair[0]} + {pair[1]}", 'count': count} for pair, count in top_pairs]
    }


def analyze_instruction_adherence(df: pd.DataFrame) -> Dict[str, Any]:
    """19. Instruction Adherence Score: Lernt der Generator aus Warnungen?"""
    if 'warnings_text' not in df.columns or 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    adherence_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) < 2:
            continue
        
        # Analysiere ob Warnungen aus Schritt n in Schritt n+1 behoben wurden
        for i in range(len(inject_df) - 1):
            prev_row = inject_df.iloc[i]
            next_row = inject_df.iloc[i+1]
            
            prev_warnings = str(prev_row.get('warnings_text', '')).lower()
            next_errors = str(next_row.get('errors_text', '')).lower()
            next_warnings = str(next_row.get('warnings_text', '')).lower()
            
            if not prev_warnings:
                continue
            
            # Extrahiere Keywords aus Warnungen
            warning_keywords = set(re.findall(r'\b\w{4,}\b', prev_warnings))  # Wörter mit 4+ Zeichen
            
            # Prüfe ob diese Keywords in nächsten Fehlern/Warnungen noch vorkommen
            next_text = next_errors + ' ' + next_warnings
            next_keywords = set(re.findall(r'\b\w{4,}\b', next_text))
            
            # Adherence: Weniger Überschneidung = besser (Generator hat gelernt)
            overlap = len(warning_keywords & next_keywords)
            adherence_score = 1 - (overlap / len(warning_keywords)) if warning_keywords else 1
            
            adherence_data.append({
                'inject_id': inject_id,
                'from_refine': prev_row['refine_count'],
                'to_refine': next_row['refine_count'],
                'adherence_score': adherence_score,
                'success': next_row.get('is_valid', False)
            })
    
    if not adherence_data:
        return {}
    
    adh_df = pd.DataFrame(adherence_data)
    
    # Korrelation zwischen Adherence und Erfolg
    if len(adh_df) > 1:
        correlation = adh_df['adherence_score'].corr(adh_df['success'].astype(float))
    else:
        correlation = 0
    
    return {
        'mean_adherence': adh_df['adherence_score'].mean(),
        'adherence_success_correlation': correlation,
        'learns_from_warnings': correlation > 0.2,
        'data': adh_df
    }


def classify_constraint_violations(df: pd.DataFrame) -> Dict[str, Any]:
    """20. Constraint Violation Taxonomy: Klassifizierung in Hard vs Soft Constraints."""
    if 'errors_text' not in df.columns or 'warnings_text' not in df.columns:
        return {}
    
    # Hard Constraint Keywords (blockierend)
    hard_constraint_keywords = [
        'existiert nicht', 'does not exist', 'not found', 'nicht verfügbar',
        'inkonsistent', 'inconsistent', 'widerspruch', 'contradiction',
        'temporal', 'zeitstempel', 'timestamp', 'chronologisch',
        'logical consistency', 'logische konsistenz'
    ]
    
    # Soft Constraint Keywords (nur Warnung)
    soft_constraint_keywords = [
        'könnte besser', 'could be better', 'optional', 'optional',
        'name mismatch', 'namensvariation', 'prüfe ob', 'check if',
        'regulatorische aspekte', 'regulatory aspects'
    ]
    
    violations = {
        'hard': [],
        'soft': [],
        'mixed': []
    }
    
    for idx, row in df.iterrows():
        error_text = str(row.get('errors_text', '')).lower()
        warning_text = str(row.get('warnings_text', '')).lower()
        combined_text = error_text + ' ' + warning_text
        
        has_hard = any(kw in combined_text for kw in hard_constraint_keywords)
        has_soft = any(kw in combined_text for kw in soft_constraint_keywords)
        
        if has_hard and has_soft:
            violations['mixed'].append({
                'inject_id': row.get('inject_id', 'unknown'),
                'refine_count': row.get('refine_count', 0)
            })
        elif has_hard:
            violations['hard'].append({
                'inject_id': row.get('inject_id', 'unknown'),
                'refine_count': row.get('refine_count', 0)
            })
        elif has_soft:
            violations['soft'].append({
                'inject_id': row.get('inject_id', 'unknown'),
                'refine_count': row.get('refine_count', 0)
            })
    
    return {
        'hard_constraints': len(violations['hard']),
        'soft_constraints': len(violations['soft']),
        'mixed': len(violations['mixed']),
        'hard_ratio': len(violations['hard']) / (len(violations['hard']) + len(violations['soft']) + len(violations['mixed'])) * 100 if (len(violations['hard']) + len(violations['soft']) + len(violations['mixed'])) > 0 else 0,
        'violations': violations
    }


# ============================================================================
# ANALYSE 21-30: AGENTEN-PERFORMANCE & QUALITÄTS-METRIKEN
# ============================================================================

def calculate_first_pass_yield(df: pd.DataFrame) -> Dict[str, Any]:
    """21. First Pass Yield: Prozentsatz der Injects ohne Korrektur."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    # Gruppiere nach Inject-ID und finde max Refine-Count
    inject_stats = df.groupby('inject_id').agg({
        'refine_count': 'max',
        'scenario_id': 'first'
    }).reset_index()
    
    total_injects = len(inject_stats)
    first_pass = len(inject_stats[inject_stats['refine_count'] == 0])
    fpy_percentage = (first_pass / total_injects * 100) if total_injects > 0 else 0
    
    # Pro Szenario
    fpy_by_scenario = {}
    for scenario_id in inject_stats['scenario_id'].unique():
        scenario_injects = inject_stats[inject_stats['scenario_id'] == scenario_id]
        scenario_fpy = len(scenario_injects[scenario_injects['refine_count'] == 0]) / len(scenario_injects) * 100 if len(scenario_injects) > 0 else 0
        fpy_by_scenario[scenario_id] = scenario_fpy
    
    return {
        'fpy_percentage': fpy_percentage,
        'first_pass_count': first_pass,
        'total_injects': total_injects,
        'fpy_by_scenario': fpy_by_scenario,
        'data': inject_stats
    }


def calculate_critic_strictness(df: pd.DataFrame) -> Dict[str, Any]:
    """22. Critic Strictness Index: Verhältnis von reject zu accept."""
    if 'decision' not in df.columns:
        return {}
    
    decisions = df['decision'].value_counts()
    rejects = decisions.get('reject', 0)
    accepts = decisions.get('accept', 0)
    
    strictness_index = (rejects / accepts) if accepts > 0 else 0
    
    # Pro Szenario
    strictness_by_scenario = {}
    for scenario_id in df['scenario_id'].unique():
        scenario_df = df[df['scenario_id'] == scenario_id]
        scenario_decisions = scenario_df['decision'].value_counts()
        scenario_rejects = scenario_decisions.get('reject', 0)
        scenario_accepts = scenario_decisions.get('accept', 0)
        scenario_strictness = (scenario_rejects / scenario_accepts) if scenario_accepts > 0 else 0
        strictness_by_scenario[scenario_id] = scenario_strictness
    
    return {
        'strictness_index': strictness_index,
        'rejects': rejects,
        'accepts': accepts,
        'strictness_by_scenario': strictness_by_scenario
    }


def calculate_correction_efficiency(df: pd.DataFrame) -> Dict[str, Any]:
    """23. Generator Correction Efficiency: P(Success | Fail)."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns or 'is_valid' not in df.columns:
        return {}
    
    efficiency_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        for i in range(len(inject_df) - 1):
            prev_row = inject_df.iloc[i]
            next_row = inject_df.iloc[i+1]
            
            if not prev_row.get('is_valid', True):  # Fehler bei Refine i
                success_next = next_row.get('is_valid', False)  # Erfolg bei Refine i+1?
                efficiency_data.append({
                    'inject_id': inject_id,
                    'from_refine': prev_row['refine_count'],
                    'to_refine': next_row['refine_count'],
                    'success': success_next,
                    'scenario_id': prev_row.get('scenario_id', 'unknown')
                })
    
    if not efficiency_data:
        return {}
    
    eff_df = pd.DataFrame(efficiency_data)
    efficiency_rate = eff_df['success'].mean() * 100 if len(eff_df) > 0 else 0
    
    # Pro Refine-Level
    efficiency_by_refine = {}
    for refine in sorted(eff_df['from_refine'].unique()):
        refine_df = eff_df[eff_df['from_refine'] == refine]
        efficiency_by_refine[int(refine)] = refine_df['success'].mean() * 100 if len(refine_df) > 0 else 0
    
    return {
        'efficiency_rate': efficiency_rate,
        'total_corrections': len(eff_df),
        'successful_corrections': eff_df['success'].sum(),
        'efficiency_by_refine': efficiency_by_refine,
        'data': eff_df
    }


def analyze_repeated_failures(df: pd.DataFrame) -> Dict[str, Any]:
    """24. Repeated Failure Rate: Wie oft wird derselbe Validierungsfehler hintereinander ausgelöst?"""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    repeated_failures = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        if len(inject_df) < 2:
            continue
        
        prev_failed_checks = set()
        
        for i in range(len(inject_df)):
            row = inject_df.iloc[i]
            
            if not row.get('is_valid', True):
                # Welche Checks sind fehlgeschlagen?
                failed_checks = set()
                if not row.get('logical_consistency', True):
                    failed_checks.add('logical')
                if not row.get('causal_validity', True):
                    failed_checks.add('causal')
                if not row.get('dora_compliance', True):
                    failed_checks.add('dora')
                
                # Prüfe ob dieselben Checks wieder fehlschlagen
                if prev_failed_checks and failed_checks == prev_failed_checks:
                    repeated_failures.append({
                        'inject_id': inject_id,
                        'refine_count': row['refine_count'],
                        'repeated_checks': list(failed_checks),
                        'scenario_id': row.get('scenario_id', 'unknown')
                    })
                
                prev_failed_checks = failed_checks
            else:
                prev_failed_checks = set()
    
    if not repeated_failures:
        return {'repeated_failures': [], 'count': 0, 'rate': 0}
    
    rep_df = pd.DataFrame(repeated_failures)
    
    # Berechne Rate
    total_failures = len(df[~df['is_valid']])
    repeated_rate = (len(repeated_failures) / total_failures * 100) if total_failures > 0 else 0
    
    # Häufigste wiederholte Checks
    all_repeated_checks = []
    for checks in rep_df['repeated_checks']:
        all_repeated_checks.extend(checks)
    check_counts = Counter(all_repeated_checks)
    
    return {
        'repeated_failures': repeated_failures,
        'count': len(repeated_failures),
        'rate': repeated_rate,
        'most_repeated_checks': dict(check_counts),
        'data': rep_df
    }


def analyze_refinement_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """25. Refinement Distribution Analysis: Histogramm/Verteilung der Refine-Counts."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    max_refines = df.groupby('inject_id')['refine_count'].max()
    
    # Statistische Eigenschaften
    mean_refines = max_refines.mean()
    median_refines = max_refines.median()
    std_refines = max_refines.std()
    
    # Prüfe auf Power-Law-Verteilung
    # Power-Law: std > mean * 1.5
    is_power_law = std_refines > mean_refines * 1.5
    
    # Verteilung
    distribution = max_refines.value_counts().sort_index().to_dict()
    
    # Pro Szenario
    distribution_by_scenario = {}
    for scenario_id in df['scenario_id'].unique():
        scenario_df = df[df['scenario_id'] == scenario_id]
        scenario_max_refines = scenario_df.groupby('inject_id')['refine_count'].max()
        distribution_by_scenario[scenario_id] = {
            'mean': scenario_max_refines.mean(),
            'median': scenario_max_refines.median(),
            'std': scenario_max_refines.std()
        }
    
    return {
        'mean': mean_refines,
        'median': median_refines,
        'std': std_refines,
        'min': max_refines.min(),
        'max': max_refines.max(),
        'distribution': distribution,
        'is_power_law': is_power_law,
        'distribution_by_scenario': distribution_by_scenario,
        'data': max_refines.reset_index()
    }


def analyze_warning_tolerance(df: pd.DataFrame) -> Dict[str, Any]:
    """26. Warning Tolerance Threshold: Wie viele Warnungen akzeptiert der Critic bevor er reject schaltet?"""
    if 'warning_count' not in df.columns or 'decision' not in df.columns:
        return {}
    
    tolerance_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        # Finde letztes Reject und vorherige Warnungen
        rejected_df = inject_df[inject_df['decision'] == 'reject']
        
        if len(rejected_df) > 0:
            last_reject = rejected_df.iloc[-1]
            prev_warnings = last_reject.get('warning_count', 0)
            
            tolerance_data.append({
                'inject_id': inject_id,
                'warnings_at_reject': prev_warnings,
                'refines_at_reject': last_reject['refine_count'],
                'scenario_id': last_reject.get('scenario_id', 'unknown')
            })
    
    if not tolerance_data:
        return {}
    
    tol_df = pd.DataFrame(tolerance_data)
    
    # Decision Boundary Analyse
    # Finde Threshold: Wie viele Warnungen führen typischerweise zu Reject?
    mean_warnings_at_reject = tol_df['warnings_at_reject'].mean()
    median_warnings_at_reject = tol_df['warnings_at_reject'].median()
    
    # Vergleich: Warnungen bei Accept vs Reject
    accepted_df = df[df['decision'] == 'accept']
    mean_warnings_at_accept = accepted_df['warning_count'].mean() if len(accepted_df) > 0 else 0
    
    threshold = mean_warnings_at_reject
    
    return {
        'mean_warnings_at_reject': mean_warnings_at_reject,
        'median_warnings_at_reject': median_warnings_at_reject,
        'mean_warnings_at_accept': mean_warnings_at_accept,
        'estimated_threshold': threshold,
        'data': tol_df
    }


def calculate_golden_path_deviation(df: pd.DataFrame) -> Dict[str, Any]:
    """27. Golden Path Deviation: Abweichung vom idealen Null-Fehler-Pfad."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    deviation_data = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        max_refines = inject_df['refine_count'].max()
        total_errors = inject_df['error_count'].sum()
        total_warnings = inject_df['warning_count'].sum()
        
        # Ideal: 0 Refines, 0 Errors, 0 Warnings
        deviation_score = max_refines * 10 + total_errors * 5 + total_warnings * 2  # Gewichtete Abweichung
        
        deviation_data.append({
            'inject_id': inject_id,
            'deviation_score': deviation_score,
            'refines': max_refines,
            'errors': total_errors,
            'warnings': total_warnings,
            'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
        })
    
    if not deviation_data:
        return {}
    
    dev_df = pd.DataFrame(deviation_data)
    
    return {
        'mean_deviation': dev_df['deviation_score'].mean(),
        'median_deviation': dev_df['deviation_score'].median(),
        'min_deviation': dev_df['deviation_score'].min(),
        'max_deviation': dev_df['deviation_score'].max(),
        'perfect_paths': len(dev_df[dev_df['deviation_score'] == 0]),
        'data': dev_df
    }


def analyze_inter_scenario_variance(df: pd.DataFrame) -> Dict[str, Any]:
    """28. Inter-Scenario Variance: Standardabweichung der Qualitätsmetriken zwischen Szenarien."""
    if 'scenario_id' not in df.columns:
        return {}
    
    scenario_metrics = {}
    
    for scenario_id in df['scenario_id'].unique():
        scenario_df = df[df['scenario_id'] == scenario_id]
        
        # Metriken pro Szenario
        max_refines = scenario_df.groupby('inject_id')['refine_count'].max().mean()
        error_rate = (~scenario_df['is_valid']).mean() * 100
        warning_rate = scenario_df['warning_count'].mean()
        fpy = len(scenario_df.groupby('inject_id')['refine_count'].max()[scenario_df.groupby('inject_id')['refine_count'].max() == 0]) / len(scenario_df.groupby('inject_id')) * 100 if len(scenario_df.groupby('inject_id')) > 0 else 0
        
        scenario_metrics[scenario_id] = {
            'mean_max_refines': max_refines,
            'error_rate': error_rate,
            'mean_warnings': warning_rate,
            'fpy': fpy
        }
    
    if len(scenario_metrics) < 2:
        return {}
    
    metrics_df = pd.DataFrame(scenario_metrics).T
    
    # Berechne Varianzen
    variances = {
        'refines_variance': metrics_df['mean_max_refines'].std(),
        'error_rate_variance': metrics_df['error_rate'].std(),
        'warnings_variance': metrics_df['mean_warnings'].std(),
        'fpy_variance': metrics_df['fpy'].std()
    }
    
    # Konsistenz-Score (invers zur Varianz)
    consistency_score = 100 - min(100, np.mean(list(variances.values())) * 10)
    
    return {
        'variances': variances,
        'consistency_score': consistency_score,
        'is_consistent': consistency_score > 70,
        'scenario_metrics': scenario_metrics,
        'data': metrics_df
    }


def analyze_worst_case(df: pd.DataFrame, percentile: float = 0.99) -> Dict[str, Any]:
    """29. Worst-Case Analysis: Untersuchung der Top-1% Injects mit den meisten Refinements."""
    if 'inject_id' not in df.columns or 'refine_count' not in df.columns:
        return {}
    
    max_refines = df.groupby('inject_id')['refine_count'].max()
    
    # Top-Percentile
    threshold = max_refines.quantile(percentile)
    worst_cases = max_refines[max_refines >= threshold]
    
    if len(worst_cases) == 0:
        return {}
    
    # Analysiere Worst Cases
    worst_case_details = []
    
    for inject_id in worst_cases.index:
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        total_errors = inject_df['error_count'].sum()
        total_warnings = inject_df['warning_count'].sum()
        error_types = set()
        
        for idx, row in inject_df.iterrows():
            if not row.get('is_valid', True):
                if not row.get('logical_consistency', True):
                    error_types.add('logical')
                if not row.get('causal_validity', True):
                    error_types.add('causal')
                if not row.get('dora_compliance', True):
                    error_types.add('dora')
        
        worst_case_details.append({
            'inject_id': inject_id,
            'max_refines': worst_cases[inject_id],
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'error_types': list(error_types),
            'scenario_id': inject_df.iloc[0].get('scenario_id', 'unknown')
        })
    
    worst_df = pd.DataFrame(worst_case_details)
    
    return {
        'threshold_refines': threshold,
        'worst_case_count': len(worst_cases),
        'mean_refines_worst': worst_cases.mean(),
        'mean_errors_worst': worst_df['total_errors'].mean() if len(worst_df) > 0 else 0,
        'worst_cases': worst_case_details,
        'data': worst_df
    }


def calculate_zero_warning_rate(df: pd.DataFrame) -> Dict[str, Any]:
    """30. Zero-Warning Rate: Anteil der perfekten Injects (keine Fehler UND keine Warnungen)."""
    if 'inject_id' not in df.columns:
        return {}
    
    perfect_injects = []
    
    for inject_id in df['inject_id'].unique():
        inject_df = df[df['inject_id'] == inject_id].sort_values(['refine_count', 'timestamp'])
        
        # Prüfe finalen Zustand
        final_state = inject_df.iloc[-1]
        
        error_count = final_state.get('error_count', 0)
        warning_count = final_state.get('warning_count', 0)
        is_valid = final_state.get('is_valid', False)
        
        if error_count == 0 and warning_count == 0 and is_valid:
            perfect_injects.append({
                'inject_id': inject_id,
                'refines': inject_df['refine_count'].max(),
                'scenario_id': final_state.get('scenario_id', 'unknown')
            })
    
    total_injects = df['inject_id'].nunique()
    zero_warning_rate = (len(perfect_injects) / total_injects * 100) if total_injects > 0 else 0
    
    return {
        'zero_warning_rate': zero_warning_rate,
        'perfect_injects_count': len(perfect_injects),
        'total_injects': total_injects,
        'perfect_injects': perfect_injects
    }


# ============================================================================
# VISUALISIERUNGEN
# ============================================================================

def plot_refinement_velocity(velocity_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Refinement Velocity."""
    if not velocity_data or 'data' not in velocity_data:
        return go.Figure()
    
    vel_df = velocity_data['data']
    
    fig = go.Figure()
    
    # Scatter Plot
    fig.add_trace(go.Scatter(
        x=vel_df['from_refine'],
        y=vel_df['time_diff_seconds'],
        mode='markers',
        name='Velocity',
        marker=dict(size=8, opacity=0.6)
    ))
    
    # Trendline
    if len(vel_df) > 1:
        z = np.polyfit(vel_df['from_refine'], vel_df['time_diff_seconds'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(vel_df['from_refine'].min(), vel_df['from_refine'].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend',
            line=dict(dash='dash', color='red')
        ))
    
    fig.update_layout(
        title="Refinement Velocity: Zeit zwischen Iterationen",
        xaxis_title="Von Refine Count",
        yaxis_title="Zeit (Sekunden)",
        height=400
    )
    
    return fig


def plot_fatigue_analysis(fatigue_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Scenario Fatigue."""
    if not fatigue_data or 'data' not in fatigue_data:
        return go.Figure()
    
    fatigue_df = fatigue_data['data']
    
    fig = go.Figure()
    
    # Plot pro Szenario
    for scenario_id in fatigue_df['scenario_id'].unique():
        scenario_data = fatigue_df[fatigue_df['scenario_id'] == scenario_id].sort_values('iteration')
        fig.add_trace(go.Scatter(
            x=scenario_data['iteration'],
            y=scenario_data['max_refines'],
            mode='lines+markers',
            name=scenario_id,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title="Scenario Fatigue: Refine-Count über Iterationen",
        xaxis_title="Iteration",
        yaxis_title="Max Refine Count",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_convergence_rate(convergence_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Convergence Rate."""
    if not convergence_data or 'data' not in convergence_data:
        return go.Figure()
    
    conv_df = convergence_data['data']
    converged_df = conv_df[conv_df['converged'] == True]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Verteilung der Refines bis Valid', 'Zeit bis Valid'),
        specs=[[{"type": "histogram"}, {"type": "scatter"}]]
    )
    
    # Histogramm
    fig.add_trace(
        go.Histogram(
            x=converged_df['refines_to_valid'],
            nbinsx=10,
            name='Refines'
        ),
        row=1, col=1
    )
    
    # Scatter Plot: Refines vs Zeit
    if len(converged_df) > 0 and converged_df['time_to_valid_seconds'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=converged_df['refines_to_valid'],
                y=converged_df['time_to_valid_seconds'],
                mode='markers',
                name='Refines vs Zeit',
                marker=dict(size=8, opacity=0.6)
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="Convergence Rate Analysis",
        height=400,
        showlegend=False
    )
    fig.update_xaxes(title_text="Refines bis Valid", row=1, col=1)
    fig.update_yaxes(title_text="Anzahl", row=1, col=1)
    fig.update_xaxes(title_text="Refines", row=1, col=2)
    fig.update_yaxes(title_text="Zeit (Sekunden)", row=1, col=2)
    
    return fig


def plot_time_to_acceptance(tta_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Time-to-Acceptance."""
    if not tta_data or 'data' not in tta_data:
        return go.Figure()
    
    tta_df = tta_data['data']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('TTA Verteilung', 'TTA vs Refines'),
        specs=[[{"type": "box"}, {"type": "scatter"}]]
    )
    
    # Boxplot
    fig.add_trace(
        go.Box(
            y=tta_df['tta_minutes'],
            name='TTA',
            boxmean='sd'
        ),
        row=1, col=1
    )
    
    # Scatter: TTA vs Refines
    fig.add_trace(
        go.Scatter(
            x=tta_df['refines'],
            y=tta_df['tta_minutes'],
            mode='markers',
            name='TTA vs Refines',
            marker=dict(size=8, opacity=0.6, color=tta_df['refines'], colorscale='Viridis')
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Time-to-Acceptance Analysis",
        height=400,
        showlegend=False
    )
    fig.update_yaxes(title_text="TTA (Minuten)", row=1, col=1)
    fig.update_xaxes(title_text="Refines", row=1, col=2)
    fig.update_yaxes(title_text="TTA (Minuten)", row=1, col=2)
    
    return fig


def plot_oscillations(oscillation_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Oszillationen."""
    if not oscillation_data or 'oscillations' not in oscillation_data or len(oscillation_data['oscillations']) == 0:
        return go.Figure()
    
    osc_df = pd.DataFrame(oscillation_data['oscillations'])
    
    fig = go.Figure()
    
    # Bar Chart: Oszillationen pro Inject
    fig.add_trace(go.Bar(
        x=osc_df['inject_id'],
        y=osc_df['oscillation_count'],
        name='Oszillationen',
        marker_color='coral'
    ))
    
    fig.update_layout(
        title="Oszillation Detection: Injects mit pendelnden Fehlerzuständen",
        xaxis_title="Inject ID",
        yaxis_title="Anzahl Oszillationen",
        height=400
    )
    
    return fig


def plot_bottlenecks(bottleneck_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Validation Bottlenecks."""
    if not bottleneck_data:
        return go.Figure()
    
    fig = go.Figure()
    
    # Bar Chart der Failure Rates
    checks = ['logical', 'causal', 'dora']
    rates = [
        bottleneck_data.get('logical_failure_rate', 0),
        bottleneck_data.get('causal_failure_rate', 0),
        bottleneck_data.get('dora_failure_rate', 0)
    ]
    
    colors = ['#ef4444', '#f59e0b', '#3b82f6']
    
    fig.add_trace(go.Bar(
        x=checks,
        y=rates,
        name='Failure Rate',
        marker_color=colors
    ))
    
    fig.update_layout(
        title="Validation Bottleneck Identification",
        xaxis_title="Validierungsschritt",
        yaxis_title="Failure Rate (%)",
        height=400
    )
    
    return fig


def plot_error_topics(topic_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Error Topics."""
    if not topic_data or 'topics' not in topic_data:
        return go.Figure()
    
    topics = topic_data['topics']
    
    fig = go.Figure()
    
    # Bar Chart für Top Words pro Topic
    for topic in topics[:5]:  # Erste 5 Topics
        fig.add_trace(go.Bar(
            x=topic['top_words'][:5],
            y=topic['top_weights'][:5],
            name=f"Topic {topic['topic_id']}"
        ))
    
    fig.update_layout(
        title="Error Topic Modeling: Top Words pro Topic",
        xaxis_title="Wörter",
        yaxis_title="Gewicht",
        height=400,
        barmode='group'
    )
    
    return fig


def plot_hallucination_entities(hallucination_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Hallucination Entities."""
    if not hallucination_data or 'hallucinated_assets' not in hallucination_data:
        return go.Figure()
    
    assets = hallucination_data['hallucinated_assets']
    
    if not assets:
        return go.Figure()
    
    # Zähle Häufigkeit pro Asset-Typ
    asset_types = Counter()
    for asset in assets:
        if asset.startswith('SRV-'):
            asset_types['Server'] += 1
        elif asset.startswith('APP-'):
            asset_types['Application'] += 1
        elif asset.startswith('DB-'):
            asset_types['Database'] += 1
        else:
            asset_types['Other'] += 1
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(asset_types.keys()),
        y=list(asset_types.values()),
        marker_color='coral'
    ))
    
    fig.update_layout(
        title="Hallucination Entities nach Asset-Typ",
        xaxis_title="Asset-Typ",
        yaxis_title="Anzahl",
        height=400
    )
    
    return fig


def plot_semantic_similarity(similarity_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Semantic Similarity."""
    if not similarity_data or 'data' not in similarity_data:
        return go.Figure()
    
    sim_df = similarity_data['data']
    
    fig = go.Figure()
    
    # Histogramm der Similarity-Scores
    fig.add_trace(go.Histogram(
        x=sim_df['mean_sequential_similarity'],
        nbinsx=20,
        name='Similarity Distribution'
    ))
    
    fig.update_layout(
        title="Semantic Similarity: Verteilung der Ähnlichkeits-Scores",
        xaxis_title="Mean Sequential Similarity",
        yaxis_title="Anzahl",
        height=400
    )
    
    return fig


def plot_mitre_mismatches(mismatch_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der MITRE Mismatches."""
    if not mismatch_data or 'top_mismatches' not in mismatch_data:
        return go.Figure()
    
    top_mismatches = mismatch_data['top_mismatches']
    
    if not top_mismatches:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[m['mitre_id'] for m in top_mismatches],
        y=[m['frequency'] for m in top_mismatches],
        marker_color='red',
        text=[m['frequency'] for m in top_mismatches],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="MITRE TTP Mismatch Frequency",
        xaxis_title="MITRE ID",
        yaxis_title="Häufigkeit",
        height=400
    )
    
    return fig


def plot_complexity_correlation(complexity_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Complexity-Error-Correlation."""
    if not complexity_data or 'data' not in complexity_data:
        return go.Figure()
    
    comp_df = complexity_data['data']
    
    fig = go.Figure()
    
    # Scatter Plot: Complexity vs Refines
    fig.add_trace(go.Scatter(
        x=comp_df['complexity_score'],
        y=comp_df['max_refines'],
        mode='markers',
        name='Complexity vs Refines',
        marker=dict(size=8, opacity=0.6)
    ))
    
    # Trendline
    if len(comp_df) > 1:
        z = np.polyfit(comp_df['complexity_score'], comp_df['max_refines'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(comp_df['complexity_score'].min(), comp_df['complexity_score'].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend',
            line=dict(dash='dash', color='red')
        ))
    
    fig.update_layout(
        title="Complexity-Error-Correlation",
        xaxis_title="Complexity Score",
        yaxis_title="Max Refines",
        height=400
    )
    
    return fig


def plot_dora_gaps(gap_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der DORA Gap Analysis."""
    if not gap_data or 'gap_analysis' not in gap_data:
        return go.Figure()
    
    gap_analysis = gap_data['gap_analysis']
    
    keywords = list(gap_analysis.keys())
    missing_counts = [gap_analysis[k]['missing'] for k in keywords]
    found_counts = [gap_analysis[k]['found'] for k in keywords]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=keywords,
        y=missing_counts,
        name='Fehlend',
        marker_color='red'
    ))
    
    fig.add_trace(go.Bar(
        x=keywords,
        y=found_counts,
        name='Gefunden',
        marker_color='green'
    ))
    
    fig.update_layout(
        title="DORA Gap Analysis: Fehlende vs Gefundene Keywords",
        xaxis_title="DORA-Aspekt",
        yaxis_title="Anzahl",
        height=500,
        barmode='group',
        xaxis_tickangle=-45
    )
    
    return fig


def plot_keyword_cooccurrence(cooccurrence_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung des Keyword Co-occurrence Networks."""
    if not cooccurrence_data or 'top_pairs' not in cooccurrence_data:
        return go.Figure()
    
    top_pairs = cooccurrence_data['top_pairs']
    
    if not top_pairs:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[p['keywords'] for p in top_pairs],
        y=[p['count'] for p in top_pairs],
        marker_color='purple',
        text=[p['count'] for p in top_pairs],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Keyword Co-occurrence Network: Top Paare",
        xaxis_title="Keyword-Paar",
        yaxis_title="Co-occurrence Count",
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig


def plot_instruction_adherence(adherence_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Instruction Adherence."""
    if not adherence_data or 'data' not in adherence_data:
        return go.Figure()
    
    adh_df = adherence_data['data']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Adherence Score Verteilung', 'Adherence vs Erfolg'),
        specs=[[{"type": "histogram"}, {"type": "scatter"}]]
    )
    
    # Histogramm
    fig.add_trace(
        go.Histogram(
            x=adh_df['adherence_score'],
            nbinsx=20,
            name='Adherence'
        ),
        row=1, col=1
    )
    
    # Scatter: Adherence vs Success
    fig.add_trace(
        go.Scatter(
            x=adh_df['adherence_score'],
            y=adh_df['success'].astype(int),
            mode='markers',
            name='Adherence vs Success',
            marker=dict(size=8, opacity=0.6)
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Instruction Adherence Score Analysis",
        height=400,
        showlegend=False
    )
    fig.update_xaxes(title_text="Adherence Score", row=1, col=1)
    fig.update_yaxes(title_text="Anzahl", row=1, col=1)
    fig.update_xaxes(title_text="Adherence Score", row=1, col=2)
    fig.update_yaxes(title_text="Erfolg (0/1)", row=1, col=2)
    
    return fig


def plot_constraint_violations(violation_data: Dict[str, Any]) -> go.Figure:
    """Visualisierung der Constraint Violations."""
    if not violation_data:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Hard Constraints', 'Soft Constraints', 'Mixed'],
        y=[
            violation_data.get('hard_constraints', 0),
            violation_data.get('soft_constraints', 0),
            violation_data.get('mixed', 0)
        ],
        marker_color=['red', 'orange', 'purple'],
        text=[
            violation_data.get('hard_constraints', 0),
            violation_data.get('soft_constraints', 0),
            violation_data.get('mixed', 0)
        ],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Constraint Violation Taxonomy",
        xaxis_title="Constraint-Typ",
        yaxis_title="Anzahl",
        height=400
    )
    
    return fig


def plot_trajectories(trajectory_data: Dict[str, Any], max_trajectories: int = 10) -> go.Figure:
    """Visualisierung der Refinement Trajectories."""
    if not trajectory_data or 'trajectories' not in trajectory_data:
        return go.Figure()
    
    trajectories = trajectory_data['trajectories'][:max_trajectories]
    
    fig = go.Figure()
    
    for traj in trajectories:
        refine_counts = [s['refine_count'] for s in traj['trajectory']]
        is_valid = [1 if s['is_valid'] else 0 for s in traj['trajectory']]
        
        fig.add_trace(go.Scatter(
            x=list(range(len(refine_counts))),
            y=refine_counts,
            mode='lines+markers',
            name=traj['inject_id'],
            line=dict(width=2),
            marker=dict(
                size=8,
                color=is_valid,
                colorscale='RdYlGn',
                showscale=False
            )
        ))
    
    fig.update_layout(
        title="Refinement Loops Trajectory (erste 10 Injects)",
        xaxis_title="Schritt",
        yaxis_title="Refine Count",
        height=500,
        hovermode='x unified'
    )
    
    return fig


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def render_dashboard_overview(df: pd.DataFrame):
    """Dashboard-Übersicht mit Key Metrics."""
    st.header("📊 Übersicht")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_events}</div>
            <div class="metric-label">Gesamt Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_injects = df['inject_id'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_injects}</div>
            <div class="metric-label">Eindeutige Injects</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if 'decision' in df.columns:
            accepted = len(df[df['decision'] == 'accept'])
        else:
            accepted = 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{accepted}</div>
            <div class="metric-label">Akzeptierte</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if 'refine_count' in df.columns:
            max_refines = df.groupby('inject_id')['refine_count'].max().mean()
        else:
            max_refines = 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{max_refines:.1f}</div>
            <div class="metric-label">Ø Max Refinements</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Kernmetriken
    st.subheader("🔍 Kernmetriken")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # First Pass Yield
        fpy = calculate_first_pass_yield(df)
        if fpy:
            st.metric("First-Pass-Yield", f"{fpy['fpy_percentage']:.1f}%")
    
    with col2:
        # Critic Strictness
        strictness = calculate_critic_strictness(df)
        if strictness:
            st.metric("Critic-Strictness", f"{strictness['strictness_index']:.3f}")
    
    with col3:
        # Zero Warning Rate
        zero_warning = calculate_zero_warning_rate(df)
        if zero_warning:
            st.metric("Zero-Warning-Rate", f"{zero_warning['zero_warning_rate']:.1f}%")
    
    st.markdown("---")
    
    # Analyse-Übersicht nach BA-Relevanz kategorisiert
    st.subheader("📋 Analysen nach BA-Relevanz")
    
    st.markdown("""
    <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid #667eea;">
        <h4 style="color: #1e293b; margin-top: 0;">🎯 Forschungsfrage der BA:</h4>
        <p style="color: #64748b; margin-bottom: 0;">
        <em>"Wie können Generative AI und Multi-Agenten-Systeme eingesetzt werden, um automatisch realistische, 
        logisch konsistente und DORA-konforme Krisenszenarien für Finanzinstitute zu generieren?"</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid-Layout mit 3 Kategorien nach Relevanz
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
            <h3 style="color: white; margin-top: 0;">⭐ Kernanalysen</h3>
            <p style="color: white; opacity: 0.9; font-size: 0.9em; margin-bottom: 10px;">Direkt zur Forschungsfrage</p>
            <ul style="color: white; opacity: 0.95; font-size: 0.9em;">
                <li><strong>First Pass Yield</strong> - Systemeffizienz</li>
                <li><strong>Critic Strictness</strong> - Validierungsqualität</li>
                <li><strong>Correction Efficiency</strong> - Refinement-Loops</li>
                <li><strong>Hallucination Entities</strong> - Logik-Guards</li>
                <li><strong>Constraint Violations</strong> - Konsistenz</li>
                <li><strong>DORA Gap Analysis</strong> - Compliance</li>
                <li><strong>Validation Bottlenecks</strong> - Systemanalyse</li>
                <li><strong>Convergence Rate</strong> - Erfolgsrate</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
            <h3 style="color: white; margin-top: 0;">📊 Unterstützende Analysen</h3>
            <p style="color: white; opacity: 0.9; font-size: 0.9em; margin-bottom: 10px;">Wichtige Metriken</p>
            <ul style="color: white; opacity: 0.95; font-size: 0.9em;">
                <li><strong>Refinement Velocity</strong> - Zeitanalyse</li>
                <li><strong>Time-to-Acceptance</strong> - Prozessdauer</li>
                <li><strong>Instruction Adherence</strong> - Lernen</li>
                <li><strong>Repeated Failures</strong> - Fehleranalyse</li>
                <li><strong>Refinement Distribution</strong> - Verteilung</li>
                <li><strong>Zero-Warning Rate</strong> - Perfekte Injects</li>
                <li><strong>Inter-Scenario Variance</strong> - Konsistenz</li>
                <li><strong>Semantic Similarity</strong> - Wiederholungen</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);">
            <h3 style="color: white; margin-top: 0;">🔬 Ergänzende Analysen</h3>
            <p style="color: white; opacity: 0.9; font-size: 0.9em; margin-bottom: 10px;">Zusätzliche Insights</p>
            <ul style="color: white; opacity: 0.95; font-size: 0.9em;">
                <li><strong>Scenario Fatigue</strong> - Ermüdung</li>
                <li><strong>Burstiness</strong> - Fehler-Cluster</li>
                <li><strong>Lag-Autokorrelation</strong> - Kaskaden</li>
                <li><strong>Oscillation Detection</strong> - Pendeln</li>
                <li><strong>Change Point Detection</strong> - Trends</li>
                <li><strong>Error Topic Modeling</strong> - Fehlertypen</li>
                <li><strong>MITRE Mismatches</strong> - TTP-Analyse</li>
                <li><strong>Complexity Correlation</strong> - Komplexität</li>
                <li><strong>Keyword Co-occurrence</strong> - Muster</li>
                <li><strong>Worst-Case Analysis</strong> - Outliers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def render_analyses_1_10(df: pd.DataFrame):
    """Rendert Analysen 1-10: Zeitanalyse & Prozess-Mining."""
    st.header("⏱️ Zeitanalyse & Prozess-Mining")
    st.markdown("**Zeitbasierte Muster und Prozessoptimierung**")
    st.markdown("---")
    
    # Grid-Layout für Analysen (SOTA: 2 Spalten)
    # Analyse 1: Refinement Velocity
    with st.expander("1. ⏱️ Refinement Velocity", expanded=False):
        st.markdown("**Durchschnittliche Zeitdauer zwischen Iteration n und n+1**")
        velocity = analyze_refinement_velocity(df)
        
        if velocity:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere Velocity", f"{velocity['mean_velocity']:.2f}s")
            with col2:
                st.metric("Median Velocity", f"{velocity['median_velocity']:.2f}s")
            with col3:
                st.metric("Std. Abweichung", f"{velocity['std_velocity']:.2f}s")
            
            fig = plot_refinement_velocity(velocity)
            st.plotly_chart(fig, width='stretch', key='chart_velocity_1')
            
            if 'by_refine' in velocity:
                st.markdown("**Velocity nach Refine-Count:**")
                for refine, stats in list(velocity['by_refine'].items())[:5]:
                    st.write(f"- Refine {refine}: {stats.get('mean', 0):.2f}s (n={stats.get('count', 0)})")
        else:
            st.warning("Keine Daten für Refinement Velocity verfügbar")
    
    # Analyse 2: Scenario Fatigue
    with st.expander("2. 📉 Scenario Fatigue Analysis", expanded=False):
        st.markdown("**Korrelation zwischen Fortschritt (iteration) und refine_count**")
        fatigue = analyze_scenario_fatigue(df)
        
        if fatigue:
            st.metric("Gesamt-Korrelation", f"{fatigue['overall_correlation']:.3f}")
            st.metric("Fatigue erkannt", "✅ Ja" if fatigue['fatigue_detected'] else "❌ Nein")
            
            fig = plot_fatigue_analysis(fatigue)
            st.plotly_chart(fig, width='stretch', key='chart_fatigue_2')
            
            if 'per_scenario_correlation' in fatigue:
                st.markdown("**Korrelation pro Szenario:**")
                for scenario, corr in fatigue['per_scenario_correlation'].items():
                    st.write(f"- {scenario}: {corr:.3f}")
        else:
            st.warning("Keine Daten für Scenario Fatigue verfügbar")
    
    # Analyse 3: Burstiness
    with st.expander("3. 💥 Burstiness of Errors", expanded=False):
        st.markdown("**Treten Fehler in Clustern auf oder gleichverteilt?**")
        burstiness = analyze_burstiness(df)
        
        if burstiness:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Burstiness Index", f"{burstiness['burstiness_index']:.3f}")
            with col2:
                st.metric("Memory Coefficient", f"{burstiness['memory_coefficient']:.3f}")
            with col3:
                st.metric("Bursty", "✅ Ja" if burstiness['is_bursty'] else "❌ Nein")
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Interpretation:</strong><br>
                - Burstiness Index > 0.5: Fehler treten in Clustern auf<br>
                - Memory Coefficient: Positive Werte = Fehler folgen auf Fehler<br>
                - Mittlere Intervalle: {burstiness['mean_interval']:.2f}s ± {burstiness['std_interval']:.2f}s
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Keine Daten für Burstiness verfügbar")
    
    # Analyse 4: Convergence Rate
    with st.expander("4. 🎯 Convergence Rate", expanded=False):
        st.markdown("**Wie schnell konvergiert ein Inject gegen is_valid=True?**")
        convergence = analyze_convergence_rate(df)
        
        if convergence:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere Refines", f"{convergence['mean_refines_to_valid']:.2f}")
            with col2:
                st.metric("Convergence Rate", f"{convergence['convergence_rate']:.1f}%")
            with col3:
                st.metric("Mittlere Zeit", f"{convergence['mean_time_to_valid']:.1f}s")
            
            fig = plot_convergence_rate(convergence)
            st.plotly_chart(fig, width='stretch', key='chart_convergence_4')
        else:
            st.warning("Keine Daten für Convergence Rate verfügbar")
    
    # Analyse 5: Lag-Autokorrelation
    with st.expander("5. 🔗 Lag-Autokorrelation", expanded=False):
        st.markdown("**Beeinflusst ein schwieriger Inject den nächsten?**")
        autocorr = analyze_lag_autocorrelation(df)
        
        if autocorr:
            st.metric("Lag-1 Autokorrelation", f"{autocorr['lag1_autocorrelation']:.3f}")
            st.metric("Kaskadeneffekt", "✅ Ja" if autocorr['has_cascade_effect'] else "❌ Nein")
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Interpretation:</strong><br>
                - Positive Korrelation: Schwierige Injects führen zu weiteren schwierigen Injects<br>
                - Negative Korrelation: System erholt sich schnell<br>
                - Aktueller Wert: {autocorr['lag1_autocorrelation']:.3f}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Keine Daten für Lag-Autokorrelation verfügbar")
    
    # Analyse 6: Time-to-Acceptance
    with st.expander("6. ⏰ Time-to-Acceptance (TTA)", expanded=False):
        st.markdown("**Gesamtzeit vom ersten Draft bis zum finalen accept**")
        tta = analyze_time_to_acceptance(df)
        
        if tta:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere TTA", f"{tta['mean_tta_minutes']:.1f} Min")
            with col2:
                st.metric("Median TTA", f"{tta['median_tta_seconds']:.1f}s")
            with col3:
                st.metric("Std. Abweichung", f"{tta['std_tta_seconds']:.1f}s")
            
            fig = plot_time_to_acceptance(tta)
            st.plotly_chart(fig, width='stretch', key='chart_tta_6')
        else:
            st.warning("Keine Daten für Time-to-Acceptance verfügbar")
    
    # Analyse 7: Oscillation Detection
    with st.expander("7. 🔄 Oscillation Detection", expanded=False):
        st.markdown("**Injects, die zwischen verschiedenen Fehlerzuständen pendeln**")
        oscillations = detect_oscillations(df)
        
        if oscillations and oscillations['count'] > 0:
            st.metric("Gefundene Oszillationen", oscillations['count'])
            st.metric("Mittlere Switches", f"{oscillations['mean_switches']:.1f}")
            
            fig = plot_oscillations(oscillations)
            st.plotly_chart(fig, width='stretch', key='chart_oscillations_7')
            
            st.markdown("**Details:**")
            osc_df = oscillations['data']
            st.dataframe(osc_df[['inject_id', 'oscillation_count', 'error_types', 'refines']], width='stretch')
        else:
            st.info("Keine Oszillationen gefunden")
    
    # Analyse 8: Validation Bottleneck
    with st.expander("8. 🚧 Validation Bottleneck Identification", expanded=False):
        st.markdown("**Welcher Validierungsschritt verzögert den Prozess am meisten?**")
        bottlenecks = identify_validation_bottlenecks(df)
        
        if bottlenecks:
            st.metric("Haupt-Bottleneck", bottlenecks['main_bottleneck'].upper())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Logical Failure Rate", f"{bottlenecks['logical_failure_rate']:.1f}%")
            with col2:
                st.metric("Causal Failure Rate", f"{bottlenecks['causal_failure_rate']:.1f}%")
            with col3:
                st.metric("DORA Failure Rate", f"{bottlenecks['dora_failure_rate']:.1f}%")
            
            fig = plot_bottlenecks(bottlenecks)
            st.plotly_chart(fig, width='stretch', key='chart_bottlenecks_8')
        else:
            st.warning("Keine Daten für Validation Bottleneck verfügbar")
    
    # Analyse 9: Change Point Detection
    with st.expander("9. 📍 Change Point Detection", expanded=False):
        st.markdown("**Zeitpunkte, an denen sich die Qualität statistisch signifikant ändert**")
        change_points = detect_change_points(df)
        
        if change_points and change_points['count'] > 0:
            st.metric("Gefundene Change Points", change_points['count'])
            
            cp_df = change_points['data']
            if len(cp_df) > 0:
                st.dataframe(cp_df[['timestamp', 'change_direction', 'success_rate_before', 'success_rate_after', 'p_value']], width='stretch')
                
                # Visualisierung
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cp_df['timestamp'],
                    y=cp_df['success_rate_after'],
                    mode='markers',
                    name='Change Points',
                    marker=dict(
                        size=12,
                        color=cp_df['change_direction'].map({'improvement': 'green', 'degradation': 'red'}),
                        symbol='diamond'
                    )
                ))
                fig.update_layout(
                    title="Change Points: Qualitätsänderungen über Zeit",
                    xaxis_title="Zeitpunkt",
                    yaxis_title="Success Rate nach Change Point",
                    height=400
                )
                st.plotly_chart(fig, width='stretch', key='chart_change_points_9_1')
        else:
            st.info("Keine signifikanten Change Points gefunden")
    
    # Analyse 10: Refinement Trajectories
    with st.expander("10. 🗺️ Refinement Loops Trajectory", expanded=False):
        st.markdown("**Visualisierung der Schleifen als gerichtete Pfade im Zustandsraum**")
        trajectories = analyze_refinement_trajectories(df)
        
        if trajectories and trajectories['count'] > 0:
            st.metric("Analysierte Trajectories", trajectories['count'])
            st.metric("Durchschnittliche Max Refines", f"{trajectories['avg_max_refines']:.1f}")
            
            fig = plot_trajectories(trajectories, max_trajectories=15)
            st.plotly_chart(fig, width='stretch', key='chart_trajectories_10')
        else:
            st.warning("Keine Daten für Trajectories verfügbar")


def render_core_analyses(df: pd.DataFrame):
    """Rendert Kernanalysen: Direkt zur BA-Forschungsfrage relevant."""
    st.header("⭐ Kernanalysen für die Bachelorarbeit")
    st.markdown("""
    **Diese Analysen sind direkt relevant für die Forschungsfrage:**
    
    *"Wie können Generative AI und Multi-Agenten-Systeme eingesetzt werden, um automatisch realistische, 
    logisch konsistente und DORA-konforme Krisenszenarien für Finanzinstitute zu generieren?"*
    """)
    st.markdown("---")
    
    # Analyse 21: First Pass Yield
    with st.expander("⭐ First Pass Yield (FPY) - Systemeffizienz", expanded=False):
        st.markdown("**Kernmetrik: Prozentsatz der Injects ohne jegliche Korrektur**")
        st.markdown("**BA-Relevanz:** Zeigt, wie effizient das Multi-Agenten-System arbeitet")
        fpy = calculate_first_pass_yield(df)
        
        if fpy:
            st.metric("First Pass Yield", f"{fpy['fpy_percentage']:.1f}%")
            st.metric("First Pass Count", f"{fpy['first_pass_count']}/{fpy['total_injects']}")
            
            if fpy.get('fpy_by_scenario'):
                st.markdown("**FPY pro Szenario:**")
                for scenario, fpy_value in fpy['fpy_by_scenario'].items():
                    st.write(f"- {scenario}: {fpy_value:.1f}%")
        else:
            st.warning("Keine Daten für First Pass Yield verfügbar")
    
    # Analyse 22: Critic Strictness
    with st.expander("⭐ Critic Strictness Index - Validierungsqualität", expanded=False):
        st.markdown("**Kernmetrik: Verhältnis von reject zu accept**")
        st.markdown("**BA-Relevanz:** Zeigt, wie streng die Logik-Guards sind")
        strictness = calculate_critic_strictness(df)
        
        if strictness:
            st.metric("Strictness Index", f"{strictness['strictness_index']:.3f}")
            st.metric("Rejects", strictness['rejects'])
            st.metric("Accepts", strictness['accepts'])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Reject', 'Accept'],
                y=[strictness['rejects'], strictness['accepts']],
                marker_color=['red', 'green']
            ))
            fig.update_layout(
                title="Critic Strictness: Reject vs Accept",
                height=400
            )
            st.plotly_chart(fig, width='stretch', key='chart_strictness_22_1')
        else:
            st.warning("Keine Daten für Critic Strictness verfügbar")
    
    # Analyse 23: Correction Efficiency
    with st.expander("⭐ Generator Correction Efficiency - Refinement-Loops", expanded=False):
        st.markdown("**Kernmetrik: Erfolgsrate nach Fehlern**")
        st.markdown("**BA-Relevanz:** Zeigt, wie gut das Refinement-Loop-System funktioniert")
        efficiency = calculate_correction_efficiency(df)
        
        if efficiency:
            st.metric("Correction Efficiency", f"{efficiency['efficiency_rate']:.1f}%")
            st.metric("Successful Corrections", f"{efficiency['successful_corrections']}/{efficiency['total_corrections']}")
            
            if efficiency.get('efficiency_by_refine'):
                st.markdown("**Efficiency nach Refine-Level:**")
                for refine, eff_rate in sorted(efficiency['efficiency_by_refine'].items()):
                    st.write(f"- Refine {refine}: {eff_rate:.1f}%")
        else:
            st.warning("Keine Daten für Correction Efficiency verfügbar")
    
    # Analyse 12: Hallucination Entities
    with st.expander("⭐ Hallucination Entity Extraction - Logik-Guards", expanded=False):
        st.markdown("**Kernmetrik: Gefundene nicht-existierende Assets**")
        st.markdown("**BA-Relevanz:** Zeigt, wie effektiv die State-Consistency-Checks sind")
        hallucinations = extract_hallucination_entities(df)
        
        if hallucinations and hallucinations['count'] > 0:
            st.metric("Gefundene Hallucination Assets", hallucinations['count'])
            st.metric("Total Unknown Mentions", hallucinations.get('total_unknown_mentions', 0))
            
            fig = plot_hallucination_entities(hallucinations)
            st.plotly_chart(fig, width='stretch', key='chart_hallucinations_12')
            
            st.markdown("**Gefundene Assets:**")
            assets_display = ', '.join(hallucinations['hallucinated_assets'][:20])
            st.write(assets_display)
        else:
            st.success("✅ Keine Hallucination Entities gefunden - Logik-Guards funktionieren!")
    
    # Analyse 20: Constraint Violations
    with st.expander("⭐ Constraint Violation Taxonomy - Konsistenz", expanded=False):
        st.markdown("**Kernmetrik: Hard vs Soft Constraint Verstöße**")
        st.markdown("**BA-Relevanz:** Zeigt, welche Art von Fehlern das System verhindert")
        violations = classify_constraint_violations(df)
        
        if violations:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Hard Constraints", violations.get('hard_constraints', 0))
            with col2:
                st.metric("Soft Constraints", violations.get('soft_constraints', 0))
            with col3:
                st.metric("Hard Ratio", f"{violations.get('hard_ratio', 0):.1f}%")
            
            fig = plot_constraint_violations(violations)
            st.plotly_chart(fig, width='stretch', key='chart_violations_20')
        else:
            st.warning("Keine Daten für Constraint Violations verfügbar")
    
    # Analyse 17: DORA Gap Analysis
    with st.expander("⭐ DORA Gap Analysis - Compliance", expanded=False):
        st.markdown("**Kernmetrik: Fehlende regulatorische Keywords**")
        st.markdown("**BA-Relevanz:** Zeigt DORA-Konformität des Systems")
        gaps = analyze_dora_gaps(df)
        
        if gaps:
            st.metric("Total Gaps", gaps.get('total_gaps', 0))
            
            fig = plot_dora_gaps(gaps)
            st.plotly_chart(fig, width='stretch', key='chart_dora_17')
            
            st.markdown("**Gap-Details:**")
            for keyword, data in gaps.get('gap_analysis', {}).items():
                if data['missing'] > 0:
                    st.write(f"- **{keyword}**: {data['missing']}x fehlend, {data['found']}x gefunden")
        else:
            st.warning("Keine Daten für DORA Gap Analysis verfügbar")
    
    # Analyse 8: Validation Bottlenecks
    with st.expander("⭐ Validation Bottleneck Identification - Systemanalyse", expanded=False):
        st.markdown("**Kernmetrik: Welcher Validierungsschritt verzögert am meisten?**")
        st.markdown("**BA-Relevanz:** Identifiziert Optimierungspotenziale im System")
        bottlenecks = identify_validation_bottlenecks(df)
        
        if bottlenecks:
            st.metric("Haupt-Bottleneck", bottlenecks['main_bottleneck'].upper())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Logical Failure Rate", f"{bottlenecks['logical_failure_rate']:.1f}%")
            with col2:
                st.metric("Causal Failure Rate", f"{bottlenecks['causal_failure_rate']:.1f}%")
            with col3:
                st.metric("DORA Failure Rate", f"{bottlenecks['dora_failure_rate']:.1f}%")
            
            fig = plot_bottlenecks(bottlenecks)
            st.plotly_chart(fig, width='stretch', key='chart_bottlenecks_8')
        else:
            st.warning("Keine Daten für Validation Bottleneck verfügbar")
    
    # Analyse 4: Convergence Rate
    with st.expander("⭐ Convergence Rate - Erfolgsrate", expanded=False):
        st.markdown("**Kernmetrik: Wie schnell wird ein Inject valide?**")
        st.markdown("**BA-Relevanz:** Zeigt die Erfolgsrate des Refinement-Prozesses")
        convergence = analyze_convergence_rate(df)
        
        if convergence:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere Refines", f"{convergence['mean_refines_to_valid']:.2f}")
            with col2:
                st.metric("Convergence Rate", f"{convergence['convergence_rate']:.1f}%")
            with col3:
                st.metric("Mittlere Zeit", f"{convergence['mean_time_to_valid']:.1f}s")
            
            fig = plot_convergence_rate(convergence)
            st.plotly_chart(fig, width='stretch', key='chart_convergence_4')
        else:
            st.warning("Keine Daten für Convergence Rate verfügbar")


def render_supporting_analyses(df: pd.DataFrame):
    """Rendert unterstützende Analysen: Wichtige Metriken für die BA."""
    st.header("📊 Unterstützende Analysen")
    st.markdown("**Wichtige Metriken, die die Kernanalysen ergänzen**")
    st.markdown("---")
    
    # Analyse 1: Refinement Velocity
    with st.expander("📊 Refinement Velocity", expanded=False):
        st.markdown("**Durchschnittliche Zeitdauer zwischen Iteration n und n+1**")
        velocity = analyze_refinement_velocity(df)
        
        if velocity:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere Velocity", f"{velocity['mean_velocity']:.2f}s")
            with col2:
                st.metric("Median Velocity", f"{velocity['median_velocity']:.2f}s")
            with col3:
                st.metric("Std. Abweichung", f"{velocity['std_velocity']:.2f}s")
            
            fig = plot_refinement_velocity(velocity)
            st.plotly_chart(fig, width='stretch', key='chart_velocity_1')
        else:
            st.warning("Keine Daten für Refinement Velocity verfügbar")
    
    # Analyse 6: Time-to-Acceptance
    with st.expander("📊 Time-to-Acceptance (TTA)", expanded=False):
        st.markdown("**Gesamtzeit vom ersten Draft bis zum finalen accept**")
        tta = analyze_time_to_acceptance(df)
        
        if tta:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere TTA", f"{tta['mean_tta_minutes']:.1f} Min")
            with col2:
                st.metric("Median TTA", f"{tta['median_tta_seconds']:.1f}s")
            with col3:
                st.metric("Std. Abweichung", f"{tta['std_tta_seconds']:.1f}s")
            
            fig = plot_time_to_acceptance(tta)
            st.plotly_chart(fig, width='stretch', key='chart_tta_6')
        else:
            st.warning("Keine Daten für Time-to-Acceptance verfügbar")
    
    # Analyse 19: Instruction Adherence
    with st.expander("📊 Instruction Adherence Score", expanded=False):
        st.markdown("**Lernt der Generator aus Warnungen?**")
        adherence = analyze_instruction_adherence(df)
        
        if adherence:
            st.metric("Mittlerer Adherence Score", f"{adherence.get('mean_adherence', 0):.3f}")
            st.metric("Korrelation Adherence-Erfolg", f"{adherence.get('adherence_success_correlation', 0):.3f}")
            st.metric("Lernt aus Warnungen", "✅ Ja" if adherence.get('learns_from_warnings') else "❌ Nein")
            
            fig = plot_instruction_adherence(adherence)
            st.plotly_chart(fig, width='stretch', key='chart_adherence_19')
        else:
            st.warning("Keine Daten für Instruction Adherence verfügbar")
    
    # Analyse 24: Repeated Failures
    with st.expander("📊 Repeated Failure Rate", expanded=False):
        st.markdown("**Wie oft wird derselbe Validierungsfehler hintereinander ausgelöst?**")
        repeated = analyze_repeated_failures(df)
        
        if repeated and repeated['count'] > 0:
            st.metric("Repeated Failures", repeated['count'])
            st.metric("Repeated Failure Rate", f"{repeated['rate']:.1f}%")
            
            if repeated.get('most_repeated_checks'):
                st.markdown("**Häufigste wiederholte Checks:**")
                for check, count in sorted(repeated['most_repeated_checks'].items(), key=lambda x: x[1], reverse=True):
                    st.write(f"- {check}: {count}x")
        else:
            st.info("Keine wiederholten Fehler gefunden")
    
    # Analyse 25: Refinement Distribution
    with st.expander("📊 Refinement Distribution Analysis", expanded=False):
        st.markdown("**Verteilung der Refine-Counts**")
        distribution = analyze_refinement_distribution(df)
        
        if distribution:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittelwert", f"{distribution['mean']:.2f}")
            with col2:
                st.metric("Median", f"{distribution['median']:.2f}")
            with col3:
                st.metric("Power-Law", "✅ Ja" if distribution['is_power_law'] else "❌ Nein")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=distribution['data']['refine_count'],
                nbinsx=20,
                name='Refinement Distribution'
            ))
            fig.update_layout(
                title="Refinement Distribution",
                xaxis_title="Max Refine Count",
                yaxis_title="Anzahl Injects",
                height=400
            )
            st.plotly_chart(fig, width='stretch', key='chart_distribution_25_1')
        else:
            st.warning("Keine Daten für Refinement Distribution verfügbar")
    
    # Analyse 30: Zero-Warning Rate
    with st.expander("📊 Zero-Warning Rate", expanded=False):
        st.markdown("**Anteil der perfekten Injects**")
        zero_warning = calculate_zero_warning_rate(df)
        
        if zero_warning:
            st.metric("Zero-Warning Rate", f"{zero_warning['zero_warning_rate']:.1f}%")
            st.metric("Perfekte Injects", f"{zero_warning['perfect_injects_count']}/{zero_warning['total_injects']}")
        else:
            st.warning("Keine Daten für Zero-Warning Rate verfügbar")
    
    # Analyse 28: Inter-Scenario Variance
    with st.expander("📊 Inter-Scenario Variance", expanded=False):
        st.markdown("**Konsistenz zwischen verschiedenen Szenarien**")
        variance = analyze_inter_scenario_variance(df)
        
        if variance:
            st.metric("Consistency Score", f"{variance['consistency_score']:.1f}/100")
            st.metric("Konsistent", "✅ Ja" if variance['is_consistent'] else "❌ Nein")
            
            if 'data' in variance and len(variance['data']) > 0:
                metrics_df = variance['data']
                fig = go.Figure()
                
                for metric in ['mean_max_refines', 'error_rate', 'mean_warnings', 'fpy']:
                    if metric in metrics_df.columns:
                        fig.add_trace(go.Bar(
                            x=metrics_df.index,
                            y=metrics_df[metric],
                            name=metric.replace('_', ' ').title()
                        ))
                
                fig.update_layout(
                    title="Qualitätsmetriken pro Szenario",
                    xaxis_title="Szenario",
                    yaxis_title="Wert",
                    height=400,
                    barmode='group'
                )
                st.plotly_chart(fig, width='stretch', key='chart_variance_28')
        else:
            st.warning("Keine Daten für Inter-Scenario Variance verfügbar")
    
    # Analyse 14: Semantic Similarity
    with st.expander("📊 Semantic Similarity Matrix", expanded=False):
        st.markdown("**Wie ähnlich sind sich Fehlertexte aufeinanderfolgender Injects?**")
        similarity = calculate_semantic_similarity(df)
        
        if similarity:
            st.metric("Mittlere Ähnlichkeit", f"{similarity.get('mean_similarity', 0):.3f}")
            st.metric("Repetitive Injects", f"{similarity.get('repetitive_injects', 0)}")
            st.metric("Repetitive Rate", f"{similarity.get('repetitive_rate', 0):.1f}%")
            
            fig = plot_semantic_similarity(similarity)
            st.plotly_chart(fig, width='stretch', key='chart_similarity_14')
        else:
            st.warning("Keine Daten für Semantic Similarity verfügbar")


def render_additional_analyses(df: pd.DataFrame):
    """Rendert ergänzende Analysen: Zusätzliche Insights für die BA."""
    st.header("🔬 Ergänzende Analysen")
    st.markdown("**Zusätzliche Insights und detaillierte Analysen**")
    st.markdown("---")
    
    # Analyse 2: Scenario Fatigue
    with st.expander("🔬 Scenario Fatigue Analysis", expanded=False):
        st.markdown("**Korrelation zwischen Fortschritt und refine_count**")
        fatigue = analyze_scenario_fatigue(df)
        
        if fatigue:
            st.metric("Gesamt-Korrelation", f"{fatigue['overall_correlation']:.3f}")
            st.metric("Fatigue erkannt", "✅ Ja" if fatigue['fatigue_detected'] else "❌ Nein")
            
            fig = plot_fatigue_analysis(fatigue)
            st.plotly_chart(fig, width='stretch', key='chart_fatigue_2')
        else:
            st.warning("Keine Daten für Scenario Fatigue verfügbar")
    
    # Analyse 3: Burstiness
    with st.expander("🔬 Burstiness of Errors", expanded=False):
        st.markdown("**Treten Fehler in Clustern auf?**")
        burstiness = analyze_burstiness(df)
        
        if burstiness:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Burstiness Index", f"{burstiness['burstiness_index']:.3f}")
            with col2:
                st.metric("Memory Coefficient", f"{burstiness['memory_coefficient']:.3f}")
            with col3:
                st.metric("Bursty", "✅ Ja" if burstiness['is_bursty'] else "❌ Nein")
        else:
            st.warning("Keine Daten für Burstiness verfügbar")
    
    # Analyse 5: Lag-Autokorrelation
    with st.expander("🔬 Lag-Autokorrelation", expanded=False):
        st.markdown("**Beeinflusst ein schwieriger Inject den nächsten?**")
        autocorr = analyze_lag_autocorrelation(df)
        
        if autocorr:
            st.metric("Lag-1 Autokorrelation", f"{autocorr['lag1_autocorrelation']:.3f}")
            st.metric("Kaskadeneffekt", "✅ Ja" if autocorr['has_cascade_effect'] else "❌ Nein")
        else:
            st.warning("Keine Daten für Lag-Autokorrelation verfügbar")
    
    # Analyse 7: Oscillation Detection
    with st.expander("🔬 Oscillation Detection", expanded=False):
        st.markdown("**Injects, die zwischen verschiedenen Fehlerzuständen pendeln**")
        oscillations = detect_oscillations(df)
        
        if oscillations and oscillations['count'] > 0:
            st.metric("Gefundene Oszillationen", oscillations['count'])
            st.metric("Mittlere Switches", f"{oscillations['mean_switches']:.1f}")
            
            fig = plot_oscillations(oscillations)
            st.plotly_chart(fig, width='stretch', key='chart_oscillations_7')
        else:
            st.info("Keine Oszillationen gefunden")
    
    # Analyse 9: Change Point Detection
    with st.expander("🔬 Change Point Detection", expanded=False):
        st.markdown("**Zeitpunkte mit statistisch signifikanten Qualitätsänderungen**")
        change_points = detect_change_points(df)
        
        if change_points and change_points['count'] > 0:
            st.metric("Gefundene Change Points", change_points['count'])
            
            cp_df = change_points['data']
            if len(cp_df) > 0:
                st.dataframe(cp_df[['timestamp', 'change_direction', 'success_rate_before', 'success_rate_after', 'p_value']], width='stretch')
        else:
            st.info("Keine signifikanten Change Points gefunden")
    
    # Analyse 10: Refinement Trajectories
    with st.expander("🔬 Refinement Loops Trajectory", expanded=False):
        st.markdown("**Visualisierung der Schleifen als gerichtete Pfade**")
        trajectories = analyze_refinement_trajectories(df)
        
        if trajectories and trajectories['count'] > 0:
            st.metric("Analysierte Trajectories", trajectories['count'])
            st.metric("Durchschnittliche Max Refines", f"{trajectories['avg_max_refines']:.1f}")
            
            fig = plot_trajectories(trajectories, max_trajectories=15)
            st.plotly_chart(fig, width='stretch', key='chart_trajectories_10')
        else:
            st.warning("Keine Daten für Trajectories verfügbar")
    
    # Analyse 11: Error Topic Modeling
    with st.expander("🔬 Error Topic Modeling", expanded=False):
        st.markdown("**Automatische Clusterung der Fehlermeldungen**")
        topics = analyze_error_topics(df, n_topics=5)
        
        if topics and 'topics' in topics:
            st.metric("Gefundene Topics", len(topics['topics']))
            st.metric("Analysierte Dokumente", topics.get('n_documents', 0))
            
            fig = plot_error_topics(topics)
            st.plotly_chart(fig, width='stretch', key='chart_topics_11')
        else:
            st.info("Nicht genug Fehlertexte für Topic Modeling verfügbar")
    
    # Analyse 13: Sentiment Analysis
    with st.expander("🔬 Sentiment Analysis der Warnungen", expanded=False):
        st.markdown("**Wird der Ton des Critics schärfer bei wiederholten Fehlern?**")
        sentiment = analyze_warning_sentiment(df)
        
        if sentiment:
            st.metric("Korrelation Refine-Sentiment", f"{sentiment.get('correlation_refine_sentiment', 0):.3f}")
            st.metric("Wird schärfer", "✅ Ja" if sentiment.get('gets_sharper') else "❌ Nein")
        else:
            st.warning("Keine Daten für Sentiment Analysis verfügbar")
    
    # Analyse 15: MITRE Mismatches
    with st.expander("🔬 MITRE TTP Mismatch Frequency", expanded=False):
        st.markdown("**Welche MITRE-Techniken werden falsch verwendet?**")
        mismatches = extract_mitre_mismatches(df)
        
        if mismatches and mismatches.get('total_mismatches', 0) > 0:
            st.metric("Total Mismatches", mismatches['total_mismatches'])
            st.metric("Unique Mismatches", mismatches['unique_mismatches'])
            
            fig = plot_mitre_mismatches(mismatches)
            st.plotly_chart(fig, width='stretch', key='chart_mitre_15')
        else:
            st.info("Keine MITRE Mismatches gefunden")
    
    # Analyse 16: Complexity Correlation
    with st.expander("🔬 Complexity-Error-Correlation", expanded=False):
        st.markdown("**Korrelation zwischen Textlänge und Refinements**")
        complexity = analyze_complexity_error_correlation(df)
        
        if complexity and 'correlations' in complexity:
            corr = complexity['correlations']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Refines vs Length", f"{corr.get('refines_vs_length', 0):.3f}")
            with col2:
                st.metric("Refines vs Avg Length", f"{corr.get('refines_vs_avg_length', 0):.3f}")
            with col3:
                st.metric("Refines vs Complexity", f"{corr.get('refines_vs_complexity', 0):.3f}")
            
            fig = plot_complexity_correlation(complexity)
            st.plotly_chart(fig, width='stretch', key='chart_complexity_16')
        else:
            st.warning("Keine Daten für Complexity-Correlation verfügbar")
    
    # Analyse 18: Keyword Co-occurrence
    with st.expander("🔬 Keyword Co-occurrence Network", expanded=False):
        st.markdown("**Welche Begriffe tauchen oft gemeinsam auf?**")
        cooccurrence = build_keyword_cooccurrence_network(df)
        
        if cooccurrence and cooccurrence.get('top_pairs'):
            st.metric("Top Co-occurrence Pairs", len(cooccurrence['top_pairs']))
            
            fig = plot_keyword_cooccurrence(cooccurrence)
            st.plotly_chart(fig, width='stretch', key='chart_cooccurrence_18')
        else:
            st.info("Keine Co-occurrence-Daten verfügbar")
    
    # Analyse 26: Warning Tolerance
    with st.expander("🔬 Warning Tolerance Threshold", expanded=False):
        st.markdown("**Wie viele Warnungen akzeptiert der Critic?**")
        tolerance = analyze_warning_tolerance(df)
        
        if tolerance:
            st.metric("Estimated Threshold", f"{tolerance['estimated_threshold']:.1f} Warnungen")
            st.metric("Mittlere Warnungen bei Reject", f"{tolerance['mean_warnings_at_reject']:.1f}")
            st.metric("Mittlere Warnungen bei Accept", f"{tolerance['mean_warnings_at_accept']:.1f}")
        else:
            st.warning("Keine Daten für Warning Tolerance verfügbar")
    
    # Analyse 27: Golden Path Deviation
    with st.expander("🔬 Golden Path Deviation", expanded=False):
        st.markdown("**Abweichung vom idealen Null-Fehler-Pfad**")
        deviation = calculate_golden_path_deviation(df)
        
        if deviation:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere Abweichung", f"{deviation['mean_deviation']:.1f}")
            with col2:
                st.metric("Perfekte Pfade", deviation['perfect_paths'])
            with col3:
                st.metric("Min Abweichung", f"{deviation['min_deviation']:.1f}")
            
            if 'data' in deviation and len(deviation['data']) > 0:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=deviation['data']['deviation_score'],
                    nbinsx=20,
                    name='Deviation Score'
                ))
                fig.update_layout(
                    title="Golden Path Deviation Distribution",
                    xaxis_title="Deviation Score",
                    yaxis_title="Anzahl Injects",
                    height=400
                )
                st.plotly_chart(fig, width='stretch', key='chart_deviation_27_1')
        else:
            st.warning("Keine Daten für Golden Path Deviation verfügbar")
    
    # Analyse 29: Worst-Case Analysis
    with st.expander("🔬 Worst-Case Analysis", expanded=False):
        st.markdown("**Top-1% Injects mit den meisten Refinements**")
        worst_case = analyze_worst_case(df, percentile=0.99)
        
        if worst_case and worst_case['worst_case_count'] > 0:
            st.metric("Worst Cases (Top 1%)", worst_case['worst_case_count'])
            st.metric("Threshold Refines", f"{worst_case['threshold_refines']:.1f}")
            st.metric("Mittlere Refines (Worst)", f"{worst_case['mean_refines_worst']:.1f}")
        else:
            st.info("Keine Worst Cases gefunden")
    
    # Grid-Layout für Analysen (SOTA: 2 Spalten)
    # Analyse 11: Error Topic Modeling
    with st.expander("11. 📚 Error Topic Modeling", expanded=False):
        st.markdown("**Automatische Clusterung der Fehlermeldungen in abstrakte Themen**")
        topics = analyze_error_topics(df, n_topics=5)
        
        if topics and 'topics' in topics:
            st.metric("Gefundene Topics", len(topics['topics']))
            st.metric("Analysierte Dokumente", topics.get('n_documents', 0))
            
            fig = plot_error_topics(topics)
            st.plotly_chart(fig, width='stretch', key='chart_topics_11')
            
            st.markdown("**Topic-Details:**")
            for topic in topics['topics']:
                st.write(f"**Topic {topic['topic_id']}:** {', '.join(topic['top_words'][:8])}")
            
            if 'topic_distribution' in topics:
                st.markdown("**Verteilung:**")
                for topic_id, count in topics['topic_distribution'].most_common():
                    st.write(f"- Topic {topic_id}: {count} Dokumente")
        elif topics and 'error' in topics:
            st.warning(f"Topic Modeling nicht möglich: {topics['error']}")
        else:
            st.info("Nicht genug Fehlertexte für Topic Modeling verfügbar")
    
    # Analyse 12: Hallucination Entity Extraction
    with st.expander("12. 👻 Hallucination Entity Extraction", expanded=False):
        st.markdown("**Extrahieren aller Asset-Namen aus Warnungen mit 'unknown asset'**")
        hallucinations = extract_hallucination_entities(df)
        
        if hallucinations and hallucinations['count'] > 0:
            st.metric("Gefundene Hallucination Assets", hallucinations['count'])
            st.metric("Total Unknown Mentions", hallucinations.get('total_unknown_mentions', 0))
            
            fig = plot_hallucination_entities(hallucinations)
            st.plotly_chart(fig, width='stretch', key='chart_hallucinations_12')
            
            st.markdown("**Gefundene Assets:**")
            assets_display = ', '.join(hallucinations['hallucinated_assets'][:20])
            st.write(assets_display)
            
            if hallucinations.get('unknown_mentions'):
                st.markdown("**Beispiel-Kontexte:**")
                for mention in hallucinations['unknown_mentions'][:5]:
                    st.code(mention['text'][:200], language=None)
        else:
            st.info("Keine Hallucination Entities gefunden")
    
    # Analyse 13: Sentiment Analysis
    with st.expander("13. 😠 Sentiment Analysis der Warnungen", expanded=False):
        st.markdown("**Wird der Ton des Critics schärfer bei wiederholten Fehlern?**")
        sentiment = analyze_warning_sentiment(df)
        
        if sentiment:
            st.metric("Korrelation Refine-Sentiment", f"{sentiment.get('correlation_refine_sentiment', 0):.3f}")
            st.metric("Wird schärfer", "✅ Ja" if sentiment.get('gets_sharper') else "❌ Nein")
            
            if 'mean_sentiment_by_refine' in sentiment:
                st.markdown("**Sentiment nach Refine-Count:**")
                for refine, score in sorted(sentiment['mean_sentiment_by_refine'].items())[:5]:
                    st.write(f"- Refine {refine}: {score:.2f}")
        else:
            st.warning("Keine Daten für Sentiment Analysis verfügbar")
    
    # Analyse 14: Semantic Similarity
    with st.expander("14. 🔄 Semantic Similarity Matrix", expanded=False):
        st.markdown("**Wie ähnlich sind sich Fehlertexte aufeinanderfolgender Injects?**")
        similarity = calculate_semantic_similarity(df)
        
        if similarity:
            st.metric("Mittlere Ähnlichkeit", f"{similarity.get('mean_similarity', 0):.3f}")
            st.metric("Repetitive Injects", f"{similarity.get('repetitive_injects', 0)}")
            st.metric("Repetitive Rate", f"{similarity.get('repetitive_rate', 0):.1f}%")
            
            fig = plot_semantic_similarity(similarity)
            st.plotly_chart(fig, width='stretch', key='chart_similarity_14')
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Interpretation:</strong><br>
                - Hohe Ähnlichkeit (>0.5): Generator wiederholt ähnliche Fehler<br>
                - Niedrige Ähnlichkeit: Generator produziert verschiedene Fehlertypen<br>
                - Repetitive Rate: {similarity.get('repetitive_rate', 0):.1f}% der Injects zeigen Wiederholungen
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Keine Daten für Semantic Similarity verfügbar")
    
    # Analyse 15: MITRE Mismatches
    with st.expander("15. 🎯 MITRE TTP Mismatch Frequency", expanded=False):
        st.markdown("**Welche MITRE-Techniken werden falsch verwendet?**")
        mismatches = extract_mitre_mismatches(df)
        
        if mismatches and mismatches.get('total_mismatches', 0) > 0:
            st.metric("Total Mismatches", mismatches['total_mismatches'])
            st.metric("Unique Mismatches", mismatches['unique_mismatches'])
            
            fig = plot_mitre_mismatches(mismatches)
            st.plotly_chart(fig, width='stretch', key='chart_mitre_15')
            
            st.markdown("**Top Mismatches:**")
            for mismatch in mismatches.get('top_mismatches', [])[:10]:
                st.write(f"- **{mismatch['mitre_id']}**: {mismatch['frequency']}x")
                if mismatch.get('sample_contexts'):
                    st.caption(f"  Beispiel: {mismatch['sample_contexts'][0][:100]}...")
        else:
            st.info("Keine MITRE Mismatches gefunden")
    
    # Analyse 16: Complexity-Error-Correlation
    with st.expander("16. 📏 Complexity-Error-Correlation", expanded=False):
        st.markdown("**Korrelation zwischen Textlänge der Fehlermeldung und Refinements**")
        complexity = analyze_complexity_error_correlation(df)
        
        if complexity and 'correlations' in complexity:
            corr = complexity['correlations']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Refines vs Length", f"{corr.get('refines_vs_length', 0):.3f}")
            with col2:
                st.metric("Refines vs Avg Length", f"{corr.get('refines_vs_avg_length', 0):.3f}")
            with col3:
                st.metric("Refines vs Complexity", f"{corr.get('refines_vs_complexity', 0):.3f}")
            
            fig = plot_complexity_correlation(complexity)
            st.plotly_chart(fig, width='stretch', key='chart_complexity_16')
        else:
            st.warning("Keine Daten für Complexity-Correlation verfügbar")
    
    # Analyse 17: DORA Gap Analysis
    with st.expander("17. 🛡️ DORA Gap Analysis", expanded=False):
        st.markdown("**Häufigkeitsanalyse fehlender regulatorischer Keywords**")
        gaps = analyze_dora_gaps(df)
        
        if gaps:
            st.metric("Total Gaps", gaps.get('total_gaps', 0))
            
            fig = plot_dora_gaps(gaps)
            st.plotly_chart(fig, width='stretch', key='chart_dora_17')
            
            st.markdown("**Gap-Details:**")
            for keyword, data in gaps.get('gap_analysis', {}).items():
                if data['missing'] > 0:
                    st.write(f"- **{keyword}**: {data['missing']}x fehlend, {data['found']}x gefunden")
        else:
            st.warning("Keine Daten für DORA Gap Analysis verfügbar")
    
    # Analyse 18: Keyword Co-occurrence
    with st.expander("18. 🔗 Keyword Co-occurrence Network", expanded=False):
        st.markdown("**Welche Begriffe tauchen oft gemeinsam in Fehlern auf?**")
        cooccurrence = build_keyword_cooccurrence_network(df)
        
        if cooccurrence and cooccurrence.get('top_pairs'):
            st.metric("Top Co-occurrence Pairs", len(cooccurrence['top_pairs']))
            
            fig = plot_keyword_cooccurrence(cooccurrence)
            st.plotly_chart(fig, width='stretch', key='chart_cooccurrence_18')
            
            st.markdown("**Top 10 Paare:**")
            for pair in cooccurrence['top_pairs'][:10]:
                st.write(f"- {pair['keywords']}: {pair['count']}x")
        else:
            st.info("Keine Co-occurrence-Daten verfügbar")
    
    # Analyse 19: Instruction Adherence
    with st.expander("19. 📖 Instruction Adherence Score", expanded=False):
        st.markdown("**Lernt der Generator aus Warnungen? Semantischer Abgleich zwischen warnings und Erfolg**")
        adherence = analyze_instruction_adherence(df)
        
        if adherence:
            st.metric("Mittlerer Adherence Score", f"{adherence.get('mean_adherence', 0):.3f}")
            st.metric("Korrelation Adherence-Erfolg", f"{adherence.get('adherence_success_correlation', 0):.3f}")
            st.metric("Lernt aus Warnungen", "✅ Ja" if adherence.get('learns_from_warnings') else "❌ Nein")
            
            fig = plot_instruction_adherence(adherence)
            st.plotly_chart(fig, width='stretch', key='chart_adherence_19')
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Interpretation:</strong><br>
                - Hoher Adherence Score: Generator ignoriert Warnungen nicht<br>
                - Positive Korrelation: Bessere Adherence führt zu mehr Erfolg<br>
                - Aktueller Wert: {adherence.get('adherence_success_correlation', 0):.3f}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Keine Daten für Instruction Adherence verfügbar")
    
    # Analyse 20: Constraint Violation Taxonomy
    with st.expander("20. ⚖️ Constraint Violation Taxonomy", expanded=False):
        st.markdown("**Klassifizierung der Fehler in Hard Constraints vs Soft Constraints**")
        violations = classify_constraint_violations(df)
        
        if violations:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Hard Constraints", violations.get('hard_constraints', 0))
            with col2:
                st.metric("Soft Constraints", violations.get('soft_constraints', 0))
            with col3:
                st.metric("Hard Ratio", f"{violations.get('hard_ratio', 0):.1f}%")
            
            fig = plot_constraint_violations(violations)
            st.plotly_chart(fig, width='stretch', key='chart_violations_20')
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Interpretation:</strong><br>
                - Hard Constraints: Blockierende Fehler (Asset existiert nicht, Logik-Fehler)<br>
                - Soft Constraints: Nur Warnungen (Name Mismatch, Optionale Verbesserungen)<br>
                - Hard Ratio: {violations.get('hard_ratio', 0):.1f}% der Verstöße sind hard constraints
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Keine Daten für Constraint Violations verfügbar")


def render_analyses_21_30(df: pd.DataFrame):
    """Rendert Analysen 21-30: Qualitätsmetriken & Performance."""
    st.header("🎯 Qualitätsmetriken & Performance")
    st.markdown("**Agent-Performance und Qualitätsbewertung**")
    st.markdown("---")
    
    # Grid-Layout für Analysen (SOTA: 2 Spalten)
    # Analyse 21: First Pass Yield
    with st.expander("21. ✅ First Pass Yield (FPY)", expanded=False):
        st.markdown("**Prozentsatz der Injects ohne jegliche Korrektur (refine_count == 0)**")
        fpy = calculate_first_pass_yield(df)
        
        if fpy:
            st.metric("First Pass Yield", f"{fpy['fpy_percentage']:.1f}%")
            st.metric("First Pass Count", f"{fpy['first_pass_count']}/{fpy['total_injects']}")
            
            # Pro Szenario
            if fpy.get('fpy_by_scenario'):
                st.markdown("**FPY pro Szenario:**")
                for scenario, fpy_value in fpy['fpy_by_scenario'].items():
                    st.write(f"- {scenario}: {fpy_value:.1f}%")
        else:
            st.warning("Keine Daten für First Pass Yield verfügbar")
    
    # Analyse 22: Critic Strictness
    with st.expander("22. 🔍 Critic Strictness Index", expanded=False):
        st.markdown("**Verhältnis von reject zu accept über alle Iterationen**")
        strictness = calculate_critic_strictness(df)
        
        if strictness:
            st.metric("Strictness Index", f"{strictness['strictness_index']:.3f}")
            st.metric("Rejects", strictness['rejects'])
            st.metric("Accepts", strictness['accepts'])
            
            # Visualisierung
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Reject', 'Accept'],
                y=[strictness['rejects'], strictness['accepts']],
                marker_color=['red', 'green']
            ))
            fig.update_layout(
                title="Critic Strictness: Reject vs Accept",
                height=400
            )
            st.plotly_chart(fig, width='stretch', key='chart_strictness_22_1')
        else:
            st.warning("Keine Daten für Critic Strictness verfügbar")
    
    # Analyse 23: Correction Efficiency
    with st.expander("23. ⚡ Generator Correction Efficiency", expanded=False):
        st.markdown("**Wahrscheinlichkeit, dass Iteration n+1 erfolgreich ist, gegeben dass n fehlgeschlagen ist**")
        efficiency = calculate_correction_efficiency(df)
        
        if efficiency:
            st.metric("Correction Efficiency", f"{efficiency['efficiency_rate']:.1f}%")
            st.metric("Successful Corrections", f"{efficiency['successful_corrections']}/{efficiency['total_corrections']}")
            
            if efficiency.get('efficiency_by_refine'):
                st.markdown("**Efficiency nach Refine-Level:**")
                for refine, eff_rate in sorted(efficiency['efficiency_by_refine'].items()):
                    st.write(f"- Refine {refine}: {eff_rate:.1f}%")
        else:
            st.warning("Keine Daten für Correction Efficiency verfügbar")
    
    # Analyse 24: Repeated Failure Rate
    with st.expander("24. 🔁 Repeated Failure Rate", expanded=False):
        st.markdown("**Wie oft wird derselbe Validierungsfehler hintereinander ausgelöst?**")
        repeated = analyze_repeated_failures(df)
        
        if repeated and repeated['count'] > 0:
            st.metric("Repeated Failures", repeated['count'])
            st.metric("Repeated Failure Rate", f"{repeated['rate']:.1f}%")
            
            if repeated.get('most_repeated_checks'):
                st.markdown("**Häufigste wiederholte Checks:**")
                for check, count in sorted(repeated['most_repeated_checks'].items(), key=lambda x: x[1], reverse=True):
                    st.write(f"- {check}: {count}x")
        else:
            st.info("Keine wiederholten Fehler gefunden")
    
    # Analyse 25: Refinement Distribution
    with st.expander("25. 📊 Refinement Distribution Analysis", expanded=False):
        st.markdown("**Histogramm/Verteilung der Refine-Counts (Power-Law vs Normalverteilung?)**")
        distribution = analyze_refinement_distribution(df)
        
        if distribution:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittelwert", f"{distribution['mean']:.2f}")
            with col2:
                st.metric("Median", f"{distribution['median']:.2f}")
            with col3:
                st.metric("Power-Law", "✅ Ja" if distribution['is_power_law'] else "❌ Nein")
            
            # Visualisierung
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=distribution['data']['refine_count'],
                nbinsx=20,
                name='Refinement Distribution'
            ))
            fig.update_layout(
                title="Refinement Distribution",
                xaxis_title="Max Refine Count",
                yaxis_title="Anzahl Injects",
                height=400
            )
            st.plotly_chart(fig, width='stretch', key='chart_distribution_25_1')
        else:
            st.warning("Keine Daten für Refinement Distribution verfügbar")
    
    # Analyse 26: Warning Tolerance
    with st.expander("26. ⚠️ Warning Tolerance Threshold", expanded=False):
        st.markdown("**Wie viele Warnungen akzeptiert der Critic bevor er auf reject schaltet?**")
        tolerance = analyze_warning_tolerance(df)
        
        if tolerance:
            st.metric("Estimated Threshold", f"{tolerance['estimated_threshold']:.1f} Warnungen")
            st.metric("Mittlere Warnungen bei Reject", f"{tolerance['mean_warnings_at_reject']:.1f}")
            st.metric("Mittlere Warnungen bei Accept", f"{tolerance['mean_warnings_at_accept']:.1f}")
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Decision Boundary:</strong><br>
                Der Critic akzeptiert typischerweise bis zu {tolerance['estimated_threshold']:.1f} Warnungen,<br>
                bevor er auf Reject schaltet.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Keine Daten für Warning Tolerance verfügbar")
    
    # Analyse 27: Golden Path Deviation
    with st.expander("27. 🏆 Golden Path Deviation", expanded=False):
        st.markdown("**Abweichung der realen Szenarien vom idealen Null-Fehler-Pfad**")
        deviation = calculate_golden_path_deviation(df)
        
        if deviation:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mittlere Abweichung", f"{deviation['mean_deviation']:.1f}")
            with col2:
                st.metric("Perfekte Pfade", deviation['perfect_paths'])
            with col3:
                st.metric("Min Abweichung", f"{deviation['min_deviation']:.1f}")
            
            # Visualisierung
            if 'data' in deviation and len(deviation['data']) > 0:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=deviation['data']['deviation_score'],
                    nbinsx=20,
                    name='Deviation Score'
                ))
                fig.update_layout(
                    title="Golden Path Deviation Distribution",
                    xaxis_title="Deviation Score",
                    yaxis_title="Anzahl Injects",
                    height=400
                )
                st.plotly_chart(fig, width='stretch', key='chart_deviation_27_1')
        else:
            st.warning("Keine Daten für Golden Path Deviation verfügbar")
    
    # Analyse 28: Inter-Scenario Variance
    with st.expander("28. 📊 Inter-Scenario Variance", expanded=False):
        st.markdown("**Standardabweichung der Qualitätsmetriken zwischen Szenarien (Konsistenzprüfung)**")
        variance = analyze_inter_scenario_variance(df)
        
        if variance:
            st.metric("Consistency Score", f"{variance['consistency_score']:.1f}/100")
            st.metric("Konsistent", "✅ Ja" if variance['is_consistent'] else "❌ Nein")
            
            st.markdown("**Varianzen:**")
            for metric, var_value in variance['variances'].items():
                st.write(f"- {metric}: {var_value:.3f}")
            
            # Visualisierung: Metriken pro Szenario
            if 'data' in variance and len(variance['data']) > 0:
                metrics_df = variance['data']
                fig = go.Figure()
                
                for metric in ['mean_max_refines', 'error_rate', 'mean_warnings', 'fpy']:
                    if metric in metrics_df.columns:
                        fig.add_trace(go.Bar(
                            x=metrics_df.index,
                            y=metrics_df[metric],
                            name=metric.replace('_', ' ').title()
                        ))
                
                fig.update_layout(
                    title="Qualitätsmetriken pro Szenario",
                    xaxis_title="Szenario",
                    yaxis_title="Wert",
                    height=400,
                    barmode='group'
                )
                st.plotly_chart(fig, width='stretch', key='chart_unknown_3031')
        else:
            st.warning("Keine Daten für Inter-Scenario Variance verfügbar")
    
    # Analyse 29: Worst-Case Analysis
    with st.expander("29. 🔴 Worst-Case Analysis", expanded=False):
        st.markdown("**Untersuchung der Top-1% Injects mit den meisten Refinements (Outlier-Profiling)**")
        worst_case = analyze_worst_case(df, percentile=0.99)
        
        if worst_case and worst_case['worst_case_count'] > 0:
            st.metric("Worst Cases (Top 1%)", worst_case['worst_case_count'])
            st.metric("Threshold Refines", f"{worst_case['threshold_refines']:.1f}")
            st.metric("Mittlere Refines (Worst)", f"{worst_case['mean_refines_worst']:.1f}")
            st.metric("Mittlere Errors (Worst)", f"{worst_case['mean_errors_worst']:.1f}")
            
            if worst_case.get('worst_cases'):
                st.markdown("**Worst Case Details:**")
                worst_df = pd.DataFrame(worst_case['worst_cases'])
                st.dataframe(worst_df[['inject_id', 'max_refines', 'total_errors', 'total_warnings', 'error_types']], width='stretch')
        else:
            st.info("Keine Worst Cases gefunden")
    
    # Analyse 30: Zero-Warning Rate
    with st.expander("30. ✨ Zero-Warning Rate", expanded=False):
        st.markdown("**Anteil der perfekten Injects (keine Fehler UND keine Warnungen)**")
        zero_warning = calculate_zero_warning_rate(df)
        
        if zero_warning:
            st.metric("Zero-Warning Rate", f"{zero_warning['zero_warning_rate']:.1f}%")
            st.metric("Perfekte Injects", f"{zero_warning['perfect_injects_count']}/{zero_warning['total_injects']}")
            
            if zero_warning.get('perfect_injects'):
                st.markdown("**Perfekte Injects:**")
                perfect_df = pd.DataFrame(zero_warning['perfect_injects'])
                st.dataframe(perfect_df[['inject_id', 'refines', 'scenario_id']], width='stretch')
        else:
            st.warning("Keine Daten für Zero-Warning Rate verfügbar")


def main():
    """Hauptfunktion des wissenschaftlichen Frontends."""
    init_session_state()
    
    # Header
    st.title("🔬 Forensic-Analyse Dashboard")
    st.markdown("**Analyse von Workflow-Logs und Agent-Entscheidungen**")
    
    # Info-Box über Tools
    with st.expander("ℹ️ Über dieses Tool", expanded=False):
        st.markdown("""
        **Dieses Dashboard verwendet Streamlit** für die interaktive Analyse von Forensic-Trace-Daten.
        
        **Verfügbare Analysen:**
        - ⏱️ **Zeitanalyse & Prozess-Mining** (10 Analysen): Zeitbasierte Muster und Prozessoptimierung
        - 📝 **Textanalyse & Semantik** (10 Analysen): NLP-basierte Textanalyse und semantische Muster
        - 🎯 **Qualitätsmetriken & Performance** (10 Analysen): Agent-Performance und Qualitätsbewertung
        
        **Alternative Tools:** Für weitere Analysen siehe `frontend/TOOLS_AND_ALTERNATIVES.md`
        """)
    
    st.markdown("---")
    
    # Sidebar: Daten laden & Navigation
    with st.sidebar:
        st.header("📁 Datenverwaltung")
        
        uploaded_file = st.file_uploader(
            "JSONL-Datei hochladen",
            type=['jsonl', 'json'],
            help="Lade eine JSONL-Datei mit Forensic-Trace-Daten",
            key="forensic_upload"
        )
        
        if uploaded_file is not None:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl', mode='w') as tmp_file:
                tmp_file.write(uploaded_file.getvalue().decode('utf-8'))
                tmp_path = tmp_file.name
            
            df = load_forensic_jsonl(tmp_path)
            if not df.empty:
                st.session_state.forensic_data = df
                st.session_state.loaded_data = True
                st.success(f"✅ {len(df)} Forensic-Events geladen")
            
            Path(tmp_path).unlink()
        
        if st.button("📂 Standard-Datei laden"):
            jsonl_paths = [
                Path("logs/forensic/forensic_trace.jsonl"),
                Path("forensic_trace.jsonl")
            ]
            loaded = False
            for jsonl_path in jsonl_paths:
                if jsonl_path.exists():
                    df = load_forensic_jsonl(str(jsonl_path))
                    if not df.empty:
                        st.session_state.forensic_data = df
                        st.session_state.loaded_data = True
                        st.success(f"✅ {len(df)} Forensic-Events geladen")
                        loaded = True
                        st.rerun()
                        break
            if not loaded:
                st.error("Standarddatei nicht gefunden")
        
        st.markdown("---")
        
        if st.session_state.loaded_data and st.session_state.forensic_data is not None:
            df = st.session_state.forensic_data
            st.info(f"**Geladene Daten:**\n- {len(df)} Events\n- {df['scenario_id'].nunique()} Szenarien\n- {df['inject_id'].nunique()} Injects")
        
        st.markdown("---")
        st.header("🧭 Navigation")
        st.markdown("""
        **Analysekategorien nach BA-Relevanz:**
        
        📊 **Übersicht** - Kernmetriken & Dashboard
        
        ⭐ **Kernanalysen** (BA-relevant)
        - First Pass Yield
        - Critic Strictness
        - Correction Efficiency
        - Hallucination Entities
        - Constraint Violations
        - DORA Gap Analysis
        - Validation Bottlenecks
        - Convergence Rate
        
        📊 **Unterstützende Analysen**
        - Refinement Velocity
        - Time-to-Acceptance
        - Instruction Adherence
        - Repeated Failures
        - Refinement Distribution
        - Zero-Warning Rate
        - Inter-Scenario Variance
        - Semantic Similarity
        
        🔬 **Ergänzende Analysen**
        - Scenario Fatigue
        - Burstiness
        - Lag-Autokorrelation
        - Oscillation Detection
        - Change Point Detection
        - Error Topic Modeling
        - MITRE Mismatches
        - Complexity Correlation
        - Keyword Co-occurrence
        - Warning Tolerance
        - Golden Path Deviation
        - Worst-Case Analysis
        """)
    
    # Main Content
    if not st.session_state.loaded_data or st.session_state.forensic_data is None:
        st.info("👈 Bitte lade zuerst eine JSONL-Datei in der Sidebar")
        return
    
    df = st.session_state.forensic_data
    
    # Tabs nach BA-Relevanz kategorisiert
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Übersicht",
        "⭐ Kernanalysen (BA-relevant)",
        "📊 Unterstützende Analysen",
        "🔬 Ergänzende Analysen"
    ])
    
    with tab1:
        render_dashboard_overview(df)
    
    with tab2:
        render_core_analyses(df)
    
    with tab3:
        render_supporting_analyses(df)
    
    with tab4:
        render_additional_analyses(df)


if __name__ == "__main__":
    main()
