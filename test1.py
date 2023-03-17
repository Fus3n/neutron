class Main:
    def __init__(self):
        self._name = "Name"

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        print("sette")
        self._name = name


m = Main()
m.name = "Asif"
print(m.name)




