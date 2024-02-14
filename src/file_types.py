from enum import Enum, auto

class FileType(Enum):
    Python = auto()
    Json = auto()
    Toml = auto()
    Other = auto()

def generate_file_mapping(file_type_extensions):
    file_mapping = {}
    for file_type, extensions in file_type_extensions.items():
        for extension in extensions:
            file_mapping[extension] = file_type
    return file_mapping

file_type_extensions = {
    FileType.Python: [".py", ".pyw"],
    FileType.Json: [".json", ".ipynb"],
    FileType.Toml: [".toml"],
    FileType.Other: [".txt"],
}

FILE_MAPPING = generate_file_mapping(file_type_extensions)

def get_file_type(file_suffix: str):
    return FILE_MAPPING.get(file_suffix, FileType.Other)
