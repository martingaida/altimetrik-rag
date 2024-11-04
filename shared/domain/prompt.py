from shared.domain.base import VectorBaseDocument
from shared.domain.cleaned_documents import CleanedECTDocument
from shared.domain.types import DataCategory


class Prompt(VectorBaseDocument):
    template: str
    input_variables: dict
    content: str
    num_tokens: int | None = None

    class Config:
        category = DataCategory.PROMPT


class GenerateDatasetSamplesPrompt(Prompt):
    data_category: DataCategory
    document: CleanedECTDocument
