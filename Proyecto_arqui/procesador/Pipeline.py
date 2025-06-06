#from procesador import ALU,DM,InstMem,RegisterFile

class Pipeline_marcador:
    def __init__(self):
        self.registros = RegisterFile()
        self.alu = ALU()
        self.dm = DM()
        self.im = InstMem()
        self.safe = SAFE()
        self.saks = SAKS()
        self.marcador = Marcador()
        self.memoria = Memoria()

    def tick(self):
        instruccion = self.im # nombre de la funcion para llamarlo
        
        if not self.marcador.puede_ejecutar(instruccion):
            print(f"Instrucción en PC={self.pc} no puede ejecutarse todavía.")
            return  # stall

        decoded = self.marcador #decodificar
        self.safe#metodo()

        if self.safe.esta_lista():
            operacion, op1, op2 = self.safe.obtener_operacion()
            resultado = self.alu.execute(operacion, op1, op2)

            destino = self.safe.obtener_destino()
            self.registros.actualizar(destino, resultado)

            self.marcador.marcar_como_terminada(instruccion)

        self.pc += 4  



    
        