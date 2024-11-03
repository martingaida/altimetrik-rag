from pathlib import Path
from typing_extensions import Annotated
from zenml import step

class JsonFileManager:
    @staticmethod
    def write(filename: Path, data: dict) -> Path:
        """Write data to a JSON file."""
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename.absolute()

@step
def to_json(
    data: Annotated[dict, "serialized_artifact"],
    to_file: Annotated[Path, "to_file"],
) -> Annotated[Path, "exported_file_path"]:
    """Export serialized data to a JSON file."""
    absolute_file_path = JsonFileManager.write(
        filename=to_file,
        data=data,
    )
    return absolute_file_path