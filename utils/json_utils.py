"""
Zentrale JSON-Utility-Funktionen für sichere Serialisierung.

Stellt Helper-Funktionen bereit, die automatisch datetime-Objekte korrekt serialisieren.
"""

import json
from datetime import datetime
from typing import Any, Dict
from utils.json_encoder import DateTimeEncoder


def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Sicheres Umwandeln in einen JSON-String (für API Responses).
    
    Verwendet automatisch DateTimeEncoder für datetime-Objekte.
    
    Args:
        data: Zu serialisierendes Objekt
        **kwargs: Zusätzliche Argumente für json.dumps
    
    Returns:
        JSON-String mit korrekt serialisierten datetime-Objekten
    """
    # Stelle sicher, dass cls=DateTimeEncoder verwendet wird
    if 'cls' not in kwargs:
        kwargs['cls'] = DateTimeEncoder
    return json.dumps(data, **kwargs)


def safe_json_dump(data: Any, file_handle, **kwargs) -> None:
    """
    Sicheres Schreiben in Dateien.
    
    Verwendet automatisch DateTimeEncoder für datetime-Objekte.
    
    Args:
        data: Zu serialisierendes Objekt
        file_handle: Datei-Handle (z.B. von open())
        **kwargs: Zusätzliche Argumente für json.dump
    """
    # Stelle sicher, dass cls=DateTimeEncoder verwendet wird
    if 'cls' not in kwargs:
        kwargs['cls'] = DateTimeEncoder
    json.dump(data, file_handle, **kwargs)


def safe_json_loads(json_str: str) -> Any:
    """
    Lädt JSON aus einem String (Wrapper für json.loads).
    
    Args:
        json_str: JSON-String
    
    Returns:
        Deserialisiertes Objekt
    """
    return json.loads(json_str)


def serialize_datetime_recursive(obj: Any) -> Any:
    """
    Rekursiv serialisiert datetime-Objekte in einem Dictionary oder einer Liste.
    
    Nützlich für komplexe verschachtelte Strukturen.
    
    Args:
        obj: Zu serialisierendes Objekt (dict, list, oder primitiv)
    
    Returns:
        Objekt mit serialisierten datetime-Objekten
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_datetime_recursive(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_recursive(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize_datetime_recursive(item) for item in obj)
    else:
        return obj

