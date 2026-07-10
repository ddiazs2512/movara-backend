from dataclasses import dataclass


@dataclass(slots=True)
class SearchContext:
    """
    Contexto completo de una búsqueda.

    Toda la inteligencia del SearchEngine
    trabaja sobre este objeto.
    """

    query: str

    latitude: float | None = None
    longitude: float | None = None

    district: str | None = None
    province: str | None = None
    department: str | None = None

    country: str = "Perú"
