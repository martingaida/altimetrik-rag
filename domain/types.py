from enum import StrEnum


class DataCategory(StrEnum):
    PROMPT = "prompt"
    QUERIES = "queries"
    EARNINGS_CALLS = "earnings_calls"
    EMBEDDED_EARNINGS_CALLS = "embedded_earnings_calls"