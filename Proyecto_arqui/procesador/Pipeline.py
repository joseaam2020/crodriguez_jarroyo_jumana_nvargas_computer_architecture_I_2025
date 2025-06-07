#from procesador import ALU,DM,InstMem,RegisterFile
from ALU import ALU
from RegisterFile import RegisterFile
from DM import DM
from InstMem import InstMem
from Safe import Safe
from SAXS import SAXS
from MemoriaCentral import CentralMemory
import procesador.Marcador as Marcador
from ParserMarcador import ScoreboardParser,Scoreboard 

class Pipeline_marcador (Scoreboard):
    _instance = None
    
    def _new_(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super()
        self.registros = RegisterFile()
        self.alu = ALU()
        self.dm = DM()
        self.im = InstMem()
        self.safe = Safe()
        self.saks = SAXS()
        #self.marcador = Marcador(scoardboard)
        self.memoria = CentralMemory()


    

