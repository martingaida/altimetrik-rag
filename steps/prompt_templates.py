from datetime import datetime
from langchain.prompts import PromptTemplate

from .base import PromptTemplateFactory


class QueryExpansionTemplateECT(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to generate {expand_to_n}
    diverse and contextually relevant versions of the given user question. These variations should help in retrieving
    relevant sections from earnings call transcripts by overcoming limitations of distance-based similarity search.
    Think creatively about different ways to phrase questions related to financial metrics, guidance, or executive commentary.
    Provide these alternative questions separated by '{separator}'.

    For example:
    Original question: "What is the revenue guidance for next quarter?"
    Expanded questions:
    1. "Can you provide the expected revenue for the upcoming quarter?"
    2. "What are the revenue projections for the next quarter?"
    3. "How does the revenue outlook for next quarter look?"

    Original question: {question}"""

    @property
    def separator(self) -> str:
        return "#next-question#"

    def create_template(self, expand_to_n: int) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={
                "separator": self.separator,
                "expand_to_n": expand_to_n,
            },
        )


class SelfQueryTemplateECT(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to extract key terms or metrics from the user's question.
    Focus on identifying financial metrics, business keywords (e.g., revenue, guidance, profit), and time references (e.g., next quarter, last year).
    If the question refers to upcoming or recent timeframes, append today's date in the format {today}.
    Your response should consist of only the extracted terms, separated by commas. If no key terms are present, return 'none'.

    Examples:
    QUESTION 1: "What is the revenue guidance for next quarter?"
    RESPONSE 1: "revenue, guidance, next quarter as of {today}"

    QUESTION 2: "Can you summarize the key metrics from this quarter?"
    RESPONSE 2: "key metrics, this quarter"

    QUESTION 3: "I’d like to know about future growth plans."
    RESPONSE 3: "growth plans"

    QUESTION 4: "Show me the company’s profit for last year."
    RESPONSE 4: "profit, last year"

    User question: {question}"""

    def create_template(self) -> PromptTemplate:
        today = datetime.today().strftime("%Y-%m-%d")
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={"today": today},
        )