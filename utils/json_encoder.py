"""
Zentrale JSON-Encoder-Klasse für DateTime-Serialisierung.

Verwendet in allen JSON-Serialisierungen, um datetime-Objekte korrekt zu handhaben.
"""

import json
from datetime import datetime
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """
    JSON-Encoder, der datetime-Objekte automatisch zu ISO-Format konvertiert.
    
    Verwendung:
        json.dumps(data, cls=DateTimeEncoder)
        json.dump(data, file, cls=DateTimeEncoder)
    """
    
    def default(self, obj: Any) -> Any:
        """
        Konvertiert datetime-Objekte zu ISO-Format-Strings.
        
        Args:
            obj: Zu serialisierendes Objekt
        
        Returns:
            ISO-Format String für datetime, sonst Standard-Verhalten
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

