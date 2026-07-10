from core.places.models import SearchContext


class QueryEnhancer:

    MIN_QUERY_LENGTH = 3

    def enhance(
        self,
        context: SearchContext
    ) -> str:

        query = context.query.strip()

        if len(query) < self.MIN_QUERY_LENGTH:
            return query

        query_lower = query.lower()

        # Si ya parece suficientemente específica,
        # no modificar.
        palabras = [
            "perú",
            "peru",
            "lima",
            "san martín",
            "san martin",
            "rioja",
            "tarapoto",
            "moyobamba",
            "cajamarca"
        ]

        if any(p in query_lower for p in palabras):
            return query

        partes = [query]

        if context.district:
            partes.append(context.district)

        if context.province and context.province != context.district:
            partes.append(context.province)

        if context.department:
            partes.append(context.department)

        partes.append(context.country)

        return ", ".join(partes)
