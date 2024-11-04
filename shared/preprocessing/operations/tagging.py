from loguru import logger

from typing import List, Dict


def get_keywords_ect() -> List[str]:
    """Return list of keywords"""
    return [
        # Financial Performance
        "revenue", "revenue growth", "revenue guidance", "quarterly revenue", "annual revenue",
        "earnings", "earnings per share", "EPS", "diluted EPS", "adjusted EPS", "profit",
        "profitability", "gross profit", "gross margin", "operating margin", "operating income",
        "net income", "income statement", "EBITDA", "adjusted EBITDA", "operating expenses",
        "OPEX", "cost of goods sold", "COGS", "net margin", "gross profit margin", "cost structure",

        # Future Outlook and Guidance
        "guidance", "financial guidance", "earnings guidance", "margin guidance",
        "financial outlook", "future outlook", "next quarter forecast", "fiscal year forecast",
        "long-term outlook", "growth forecast", "expected growth", "projected revenue",
        "projected growth", "full-year forecast", "long-term targets", "guidance range",
        "annual guidance",

        # Market Conditions and External Factors
        "market conditions", "economic environment", "market demand", "customer demand",
        "industry trends", "macroeconomic factors", "supply chain", "inflation impact",
        "currency exchange", "foreign exchange impact", "competitive landscape", "regulatory environment",
        "geopolitical impact", "consumer behavior", "market share", "competitive positioning",

        # Product and Innovation
        "product innovation", "product roadmap", "new product launch", "product updates",
        "product pipeline", "R&D", "AI initiatives", "artificial intelligence", "technology investment",
        "digital transformation", "software updates", "platform capabilities", "data analytics",
        "machine learning", "product adoption", "customer experience",

        # Operational Performance
        "operational efficiency", "cost-cutting measures", "expense reduction", "headcount changes",
        "workforce optimization", "operational excellence", "productivity improvements", "cost management",
        "operational challenges", "business restructuring", "optimization initiatives", "expense controls",
        "overhead reduction",

        # Sales and Customer Metrics
        "customer retention", "customer acquisition", "customer growth", "sales growth",
        "sales pipeline", "sales forecast", "new customer wins", "churn rate", "subscription renewals",
        "contract value", "average contract value", "ACV", "annual recurring revenue", "ARR",
        "monthly recurring revenue", "MRR", "customer satisfaction", "net promoter score", "NPS",

        # Cash Flow and Capital Structure
        "cash flow", "free cash flow", "operating cash flow", "capital expenditures", "CapEx",
        "return on capital", "capital allocation", "debt reduction", "leverage ratio", "balance sheet",
        "cash reserves", "cash position", "working capital", "liquidity", "financial flexibility",

        # Financial Reporting and Accounting
        "financial reporting", "accounting standards", "GAAP", "non-GAAP", "IFRS", "SEC filings", "10-K", "10-Q",
        "audited financials", "audit report", "financial audit", "financial statements", "financial analysis",
        "audit", "amortization", "depreciation", "accrual accounting", "EBITDA adjustment", "tax provisions",
        "reconciliations"

        # Shareholder Returns
        "dividend", "dividend payout", "dividend yield", "stock repurchase", "share buyback",
        "total shareholder return", "TSR", "capital return to shareholders", "stock performance",
        "return on equity", "ROE", "return on investment", "ROI", "equity value",

        # Mergers, Acquisitions, and Partnerships
        "acquisition", "merger", "strategic partnership", "joint venture", "investment", "divestiture",
        "corporate restructuring", "business combination", "synergies", "integration progress",
        "partnership opportunities",

        # Risk Factors and Challenges
        "risk management", "financial risks", "operational risks", "market risks", "cybersecurity",
        "regulatory risks", "supply chain risks", "inflation risk", "interest rate impact",
        "currency fluctuations", "economic downturn", "industry-specific risks", "litigation",
        "regulatory compliance",

        # Corporate Governance and Leadership
        "leadership changes", "board of directors", "CEO commentary", "CFO commentary",
        "COO commentary", "management priorities", "corporate governance", "corporate responsibility",
        "executive transition", "organizational structure", "CEO", "CFO", "COO", "CRO", "CMO", "CTO", "CIO",
        "chairman", "chairperson", "chairwoman",

        # Sustainability and Corporate Responsibility
        "environmental impact", "sustainability goals", "corporate social responsibility", "CSR",
        "climate change initiatives", "carbon footprint", "renewable energy", "ESG", "community engagement",
        "diversity and inclusion", "D&I", "sustainable practices", "net zero targets",

        # Q&A and Analyst Interactions
        "question and answer session", "analyst questions", "follow-up questions", "analyst feedback",
        "earnings call Q&A", "investor relations", "shareholder questions",

        # General and Miscellaneous Phrases
        "fiscal year", "quarterly results", "financial highlights", "key takeaways", "year-over-year comparison",
        "YoY", "sequential growth", "year-to-date performance", "seasonality impact", "key metrics", "strategy",
        "strategic initiatives", "strategic plan", "strategic direction", "strategic priorities", "strategic goals"
]


def tag_chunk(text: str, keywords: List[str] = get_keywords_ect()) -> List[str]:
    """Tag chunk based on keyword presence"""
    text = text.lower()
    tags = []
   
    for keyword in keywords:
        if keyword in text:
            tags.append(keyword)
            
    return tags 
