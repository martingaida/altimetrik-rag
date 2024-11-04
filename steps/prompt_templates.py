from datetime import datetime
from langchain.prompts import PromptTemplate

from .base import PromptTemplateFactory


class QueryExpansionTemplateECT(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to generate {expand_to_n}
    different versions of the given user question to retrieve relevant sections from earnings call transcripts.
    By generating multiple perspectives on the user question, your goal is to help the user overcome some limitations
    of the distance-based similarity search. Think of different ways to phrase questions about financial metrics,
    guidance, or executive commentary in the earnings calls.
    Provide these alternative questions separated by '{separator}'.
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
    prompt: str = """You are an AI language model assistant. Your task is to extract relevant key terms or metrics from the user's question.
    The required information that needs to be extracted includes metrics, financial terms, specific business keywords (e.g., revenue, guidance, profit), or time references (e.g., next quarter, last year).
    Additionally, if the question refers to upcoming or recent timeframes (e.g., "next quarter," "this year"), append today's date in the format {today}.
    Your response should consist of only the extracted term(s) (e.g., revenue, guidance, next quarter as of {today}) separated by commas.
    If the user question does not contain any key terms, you should return the following token: none.
    
    For example:
    QUESTION 1:
    What is the revenue guidance for next quarter?
    RESPONSE 1:
    revenue, guidance, next quarter as of {today}
    
    QUESTION 2:
    Can you summarize the key metrics from this quarter?
    RESPONSE 2:
    key metrics, this quarter
    
    QUESTION 3:
    I’d like to know about future growth plans.
    RESPONSE 3:
    growth plans
    
    QUESTION 4:
    Show me the company’s profit for last year.
    RESPONSE 4:
    profit, last year
    
    User question: {question}"""

    def create_template(self) -> PromptTemplate:
        today = datetime.today().strftime("%Y-%m-%d")
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={"today": today},
        )