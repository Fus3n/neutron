from PyQt5.QtCore import QThread
from PyQt5.Qsci import QsciAPIs
from jedi import Script
from jedi.api import Completion

class AutoCompleter(QThread):
    def __init__(self, file_path, api):
        super(AutoCompleter, self).__init__(None)
        
        self.file_path = file_path
        self.script: Script = None
        self.api: QsciAPIs = api
        self.completions: list[Completion] = None

        self.line = 0
        self.index = 0
        self.text = ""


    def run(self):
        try:
            self.script: Script =  Script(self.text, path=self.file_path)
            self.completions: list[Completion] = self.script.complete(self.line, self.index)
            self.load_autocomplete(self.completions)
        except Exception as err:
            print("Autocomplete Error:", err)
        
        self.finished.emit()


    def load_autocomplete(self, completions: list[Completion]):
        self.api.clear()
        [self.api.add(i.name) for i in completions]
        self.api.prepare()

    def get_completion(self, line: int, index: int, text: str):
        self.line = line
        self.index = index
        self.text = text
        self.start()