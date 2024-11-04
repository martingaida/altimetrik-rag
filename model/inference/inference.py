import openai
from settings import settings


class LLMInferenceOpenAI:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def generate(self, prompt: str) -> str:
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert assistant specializing in financial analysis and business insights. Use the provided context to answer questions accurately and concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class InferenceExecutor:
    def __init__(self, llm: LLMInferenceOpenAI, query: str, context: str | None):
        self.llm = llm
        self.query = query
        self.context = context

    def execute(self) -> str:
        if not self.context:
            return "I apologize, but I couldn't find relevant information to answer your question."
            
        prompt = self._build_prompt()
        return self.llm.generate(prompt)

    def _build_prompt(self) -> str:
        return f"""Please use the following context to provide a detailed and accurate answer to the question. If the context is insufficient, indicate that clearly.

Context:
{self.context}

Question:
{self.query}

Answer:"""