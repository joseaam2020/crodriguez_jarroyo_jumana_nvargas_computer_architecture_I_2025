class InstMem:
    def __init__(self):
        self.memory = []

    def load_instructions(self, instructions):
        self.memory = instructions

    def fetch(self, address):
        index = address // 4  
        if index < 0 or index >= len(self.memory):
            raise IndexError("No existen mas instrucciones")
        return self.memory[index]

# Crear instancia
imem = InstMem()


instrucciones = [
    "1111111111111111111111111",    
    "0000000001111111111111100", 
    "0000000111111111111111100",          
    "1111111000000000000000000"   
]
imem.load_instructions(instrucciones)

pc = 0
inst = imem.fetch(pc)
#print(f"Instrucción en dirección {pc}: {inst}")
pc = 12
inst = imem.fetch(pc)
#print(f"Instrucción en dirección {pc}: {inst}")