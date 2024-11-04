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
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
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
        prompt = self._build_prompt()
        return self.llm.generate(prompt)

    def _build_prompt(self) -> str:
        if self.context:
            return f"""Please answer the following question based on the provided context.
                
    Context:
    {self.context}

    Question:
    {self.query}

    Answer:"""
        return f"Please answer the following question: {self.query}"