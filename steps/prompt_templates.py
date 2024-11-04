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
    prompt: str = """You are an AI language model assistant. Extract key financial terms, metrics, and time references from the user's question.
    - Financial terms include metrics like revenue, earnings, guidance, profit, and other common financial indicators.
    - Time references include specific periods like "next quarter," "last year," "this quarter." If a future or recent timeframe is mentioned, also note today’s date as {today}.
    
    Your response should list only the extracted terms and phrases separated by commas. If the question contains no relevant terms, respond with 'none'.

    Examples:
    QUESTION 1: "What is the revenue guidance for next quarter?"
    RESPONSE 1: "revenue, guidance, next quarter, {today}"

    QUESTION 2: "Can you summarize the key metrics from this quarter?"
    RESPONSE 2: "key metrics, this quarter"

    QUESTION 3: "I’d like to know about future growth plans."
    RESPONSE 3: "growth plans"

    QUESTION 4: "Show me the company’s profit for last year."
    RESPONSE 4: "profit, last year"

    QUESTION 5: "How has the company performed recently?"
    RESPONSE 5: "performance, recent, {today}"

    QUESTION 6: "What are the latest earnings figures?"
    RESPONSE 6: "earnings, latest"

    User question: {question}"""

    def create_template(self) -> PromptTemplate:
        today = datetime.today().strftime("%Y-%m-%d")
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={"today": today},
        )


class IntentDetectionTemplate(PromptTemplateFactory):
    def create_template(self) -> PromptTemplate:
        """Create intent detection prompt template"""
        # TODO COMPANY_TIMEFRAME should return document ids so that we can retrieve the documents from the vector database
        template = """Analyze the following query and determine if it matches one of these intents:

        1. METADATA: Questions about document metadata, such as page counts, document dates, types, and other details.

        If the intent is METADATA, construct an appropriate MongoDB query to retrieve data.

        Query: {question}

        Respond in JSON format:
        {{
            "intent": "INTENT_CATEGORY",
            "reasoning": "Brief explanation of why this intent was chosen",
            "mongo_query": {{
                // Construct the MongoDB query if the intent is COMPANY_TIMEFRAME, COMPANY_TOPIC, or METADATA, else return null
            }}
        }}

        Example responses:

        For "How many pages are in the most recent earnings call?":
        {{
            "intent": "METADATA",
            "reasoning": "The query requests metadata on the page count for the latest earnings call document.",
            "mongo_query": {{
                "metadata.type": "earnings_call",
                "metadata.ingestion_timestamp": {{
                    "$sort": -1
                }},
                "metadata.page_count": {{}}
            }}
        }}

        For "How many earnings call documents do you have indexed?":
        {{
            "intent": "METADATA",
            "reasoning": "The query requests a count of indexed earnings call documents.",
            "mongo_query": {{
                "metadata.type": "earnings_call",
                "$count": "document_count"
            }}
        }}

        Only respond with JSON in the specified format, without additional text or explanations.
        """

        return PromptTemplate(
            template=template,
            input_variables=["question"]
        )