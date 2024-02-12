from enum import Enum, auto

class FileType(Enum):
    Python = auto()
    Json = auto()
    Other = auto()


FILE_MAPPING = {
    ".py": FileType.Python,
    ".json": FileType.Json,
    ".txt": FileType.Other,   
}

def get_file_type(file_suffix: str):
    return FILE_MAPPING.get(file_suffix, FileType.Other)