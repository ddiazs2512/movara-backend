# ==========================================
# MOVARA CORE CONFIG
# ==========================================

# --------------------------
# CACHE
# --------------------------

CACHE_ENABLED = True

CACHE_PROVIDER = "memory"

# --------------------------
# GEOHASH
# --------------------------

GEOHASH_PRECISION = 6

# --------------------------
# TTL (segundos)
# --------------------------

REVERSE_CACHE_TTL = 86400      # 24 horas

PLACES_CACHE_TTL = 600         # 10 minutos

DIRECTIONS_CACHE_TTL = 1800    # 30 minutos

# --------------------------
# DRIVER CACHE
# --------------------------

DRIVER_REVERSE_SECONDS = 30

DRIVER_REVERSE_DISTANCE = 50

# --------------------------
# RATE LIMIT
# --------------------------

MAX_PROVIDER_REQUESTS_PER_MINUTE = 500

# --------------------------
# PROVIDERS
# --------------------------

PRIMARY_PLACES_PROVIDER = "google"

PRIMARY_REVERSE_PROVIDER = "mapbox"

PRIMARY_DIRECTIONS_PROVIDER = "mapbox"

FALLBACK_PROVIDER = "nominatim"

# --------------------------
# ANALYTICS
# --------------------------

ENABLE_ANALYTICS = True
