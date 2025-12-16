"""
Retry-Handler für robuste LLM-API-Calls.

Implementiert Retry-Logik mit Exponential Backoff für:
- OpenAI API Calls
- Neo4j Queries
- Andere externe API-Calls
"""

from typing import Callable, TypeVar, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import logging
from openai import RateLimitError, APIError, APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)

T = TypeVar('T')

# OpenAI-spezifische Fehler, die retried werden sollten
OPENAI_RETRYABLE_ERRORS = (
    RateLimitError,
    APIError,
    APIConnectionError,
    APITimeoutError,
    ConnectionError,
    TimeoutError
)


def retry_llm_call(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0
) -> Callable:
    """
    Decorator für LLM-API-Calls mit Retry-Logik.
    
    Args:
        max_attempts: Maximale Anzahl Versuche
        initial_wait: Initiale Wartezeit in Sekunden
        max_wait: Maximale Wartezeit in Sekunden
        exponential_base: Basis für exponentielles Backoff
    
    Returns:
        Decorator-Funktion
    """
    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=initial_wait,
            max=max_wait,
            exp_base=exponential_base
        ),
        retry=retry_if_exception_type(OPENAI_RETRYABLE_ERRORS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )
    def _retry_wrapper(func: Callable[..., T]) -> Callable[..., T]:
        """Wrapper für die Funktion."""
        return func
    
    return _retry_wrapper


def safe_llm_call(
    func: Callable[..., T],
    *args,
    max_attempts: int = 3,
    default_return: Optional[T] = None,
    **kwargs
) -> Optional[T]:
    """
    Führt eine LLM-Call-Funktion mit Retry-Logik aus.
    
    Args:
        func: Die aufzurufende Funktion
        *args: Positionale Argumente
        max_attempts: Maximale Anzahl Versuche
        default_return: Rückgabewert bei Fehler
        **kwargs: Keyword-Argumente
    
    Returns:
        Ergebnis der Funktion oder default_return bei Fehler
    """
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except OPENAI_RETRYABLE_ERRORS as e:
            last_exception = e
            if attempt < max_attempts:
                wait_time = min(2.0 ** attempt, 60.0)  # Exponential backoff, max 60s
                logger.warning(f"LLM-Call Versuch {attempt}/{max_attempts} fehlgeschlagen: {e}. Warte {wait_time:.1f}s...")
                import time
                time.sleep(wait_time)
            else:
                logger.error(f"LLM-Call fehlgeschlagen nach {max_attempts} Versuchen: {e}")
        except Exception as e:
            # Nicht-retryable Fehler
            logger.error(f"LLM-Call Fehler (nicht retryable): {e}")
            raise
    
    logger.error(f"LLM-Call fehlgeschlagen nach {max_attempts} Versuchen. Letzter Fehler: {last_exception}")
    return default_return


def retry_neo4j_call(
    max_attempts: int = 3,
    initial_wait: float = 0.5,
    max_wait: float = 10.0
) -> Callable:
    """
    Decorator für Neo4j-Operationen mit Retry-Logik.
    
    Args:
        max_attempts: Maximale Anzahl Versuche
        initial_wait: Initiale Wartezeit in Sekunden
        max_wait: Maximale Wartezeit in Sekunden
    
    Returns:
        Decorator-Funktion
    """
    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=initial_wait,
            max=max_wait
        ),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _retry_wrapper(func: Callable[..., T]) -> Callable[..., T]:
        return func
    
    return _retry_wrapper

