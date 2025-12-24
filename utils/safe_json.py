"""
Sichere JSON-Serialisierung für CRUX Backend.

Stellt sicher, dass alle DateTime-Objekte und Pydantic-Modelle
korrekt zu JSON serialisiert werden können.
"""

import json
from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel
from utils.json_encoder import DateTimeEncoder


def safe_json_dumps(obj: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """
    Sichere JSON-Serialisierung mit DateTime-Support.
    
    Args:
        obj: Zu serialisierendes Objekt (kann Pydantic-Modelle, Dicts, Lists enthalten)
        indent: Einrückung für formatiertes JSON
        ensure_ascii: Ob ASCII-only Encoding verwendet werden soll
    
    Returns:
        JSON-String mit korrekt serialisierten DateTime-Objekten
    """
    # Konvertiere Pydantic-Modelle zu Dicts
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode='json')
    elif isinstance(obj, list):
        obj = [item.model_dump(mode='json') if isinstance(item, BaseModel) else item for item in obj]
    elif isinstance(obj, dict):
        obj = {k: (v.model_dump(mode='json') if isinstance(v, BaseModel) else v) for k, v in obj.items()}
    
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii, cls=DateTimeEncoder)


def safe_model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """
    Konvertiert ein Pydantic-Modell sicher zu einem Dict.
    
    Args:
        model: Pydantic-Modell
    
    Returns:
        Dict mit serialisierten Werten (DateTime als ISO-String)
    """
    return model.model_dump(mode='json')


def safe_models_to_list(models: List[BaseModel]) -> List[Dict[str, Any]]:
    """
    Konvertiert eine Liste von Pydantic-Modellen sicher zu einer Liste von Dicts.
    
    Args:
        models: Liste von Pydantic-Modellen
    
    Returns:
        Liste von Dicts mit serialisierten Werten
    """
    return [model.model_dump(mode='json') for model in models]

