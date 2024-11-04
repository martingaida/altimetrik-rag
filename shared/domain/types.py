from enum import Enum


class DataCategory(Enum):
    QUERIES = "queries"
    EARNINGS_CALLS = "earnings_calls"

class QueryIntent(Enum):
    METADATA = "metadata"
    COMPANY_TIMEFRAME = "company_timeframe"
    COMPANY_TOPIC = "company_topic"
    GENERAL = "general"