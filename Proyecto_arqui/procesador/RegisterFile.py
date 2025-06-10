class RegisterFile:
    def __init__(self):
        self.regs = [i * 0 for i in range(16)]  
        self.rs1 = 0
        self.rs2 = 0
        self.rd = 0
        self.w_data = 0
        self.w_enable = False
        self.data1 = 0
        self.data2 = 0

    def write(self): # escribir
        if self.w_enable and self.rd != 0:
            self.regs[self.rd] = self.w_data 

    def read(self): # leer
        # R0 siempre es 0
        self.data1 = 0 if self.rs1 == 0 else self.regs[self.rs1]
        self.data2 = 0 if self.rs2 == 0 else self.regs[self.rs2]

    def set_inputs(self, rs1, rs2, rd, w_data, w_enable):
        self.rs1 = rs1
        self.rs2 = rs2
        self.rd = rd
        self.w_data = w_data
        self.w_enable = w_enable

    def dump(self):
        # para mostrar todos los registros
        for i in range(16):
            print(f"R{i}: {self.regs[i] & 0xFFFFFFFF}")

"""rf = RegisterFile()

rf.set_inputs(rs1=2, rs2=3, rd=5, w_data=123, w_enable=True)
rf.write()

rf.set_inputs(rs1=2, rs2=5, rd=0, w_data=0, w_enable=False)
rf.read()

# Ver valores leídos
print("Data1 (R2):", rf.data1)
print("Data2 (R5):", rf.data2)

rf.dump()"""