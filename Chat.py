"""
Analizador de rendimiento del algoritmo TEA (Tiny Encryption Algorithm)
para múltiples microarquitecturas: Uniciclo, Pipeline, VLIW, Superescalar, Multiciclo
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import pandas as pd

class InstructionType(Enum):
    LOAD = "LOAD"
    STOR = "STOR"
    DLT = "DLT"
    STK = "STK"
    SAXS = "SAXS"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    XOR = "XOR"
    AND = "AND"
    OR = "OR"
    SHRL = "SHRL"
    SHLL = "SHLL"
    LOOP = "LOOP"

@dataclass
class Instruction:
    type: InstructionType
    operands: List[str]
    cycles_base: int
    memory_access: bool = False
    branch: bool = False
    arithmetic: bool = False
    
class TEACode:
    """Representa el código TEA con sus instrucciones"""
    
    def __init__(self):
        self.instructions = []
        self._build_tea_code()
    
    def _build_tea_code(self):
        # Inicialización (5 instrucciones)
        init_instructions = [
            Instruction(InstructionType.LOAD, ["R10", "memv", "#0"], 25, memory_access=True),
            Instruction(InstructionType.LOAD, ["R11", "memv", "#4"], 25, memory_access=True),
            Instruction(InstructionType.DLT, ["R5"], 20, memory_access=True),
            Instruction(InstructionType.MUL, ["R15", "R5", "#32"], 15, arithmetic=True),
            Instruction(InstructionType.ADD, ["R7", "R7", "#32"], 6, arithmetic=True)
        ]
        
        # Loop principal (11 instrucciones × 32 iteraciones)
        loop_instructions = [
            # Calcular v1
            Instruction(InstructionType.SAXS, ["R8", "R10", "keyH"], 12, arithmetic=True),
            Instruction(InstructionType.ADD, ["R6", "R10", "R15"], 6, arithmetic=True),
            Instruction(InstructionType.XOR, ["R12", "R8", "R6"], 5, arithmetic=True),
            Instruction(InstructionType.SUB, ["R11", "R11", "R12"], 6, arithmetic=True),
            # Calcular v0
            Instruction(InstructionType.SAXS, ["R8", "R11", "keyL"], 12, arithmetic=True),
            Instruction(InstructionType.ADD, ["R6", "R11", "R15"], 6, arithmetic=True),
            Instruction(InstructionType.XOR, ["R12", "R8", "R6"], 5, arithmetic=True),
            Instruction(InstructionType.SUB, ["R10", "R10", "R12"], 6, arithmetic=True),
            # Actualizar contadores
            Instruction(InstructionType.SUB, ["R15", "R15", "R5"], 6, arithmetic=True),
            Instruction(InstructionType.SUB, ["R7", "R7", "#1"], 6, arithmetic=True),
            Instruction(InstructionType.LOOP, ["R7", "*desencriptar"], 10, branch=True)
        ]
        
        # Finalización (3 instrucciones)
        final_instructions = [
            Instruction(InstructionType.LOOP, ["R0", "*end"], 10, branch=True),
            Instruction(InstructionType.STOR, ["R10", "memv", "#0"], 30, memory_access=True),
            Instruction(InstructionType.STOR, ["R11", "memv", "#4"], 30, memory_access=True)
        ]
        
        # Construir secuencia completa
        self.instructions = init_instructions.copy()
        for _ in range(32):  # 32 iteraciones del loop
            self.instructions.extend(loop_instructions)
        self.instructions.extend(final_instructions)

class Architecture:
    """Clase base para arquitecturas"""
    
    def __init__(self, name: str):
        self.name = name
        self.total_cycles = 0
        self.total_instructions = 0
        
    def analyze(self, tea_code: TEACode) -> Dict:
        raise NotImplementedError

class UnicicloArch(Architecture):
    """Arquitectura Uniciclo - 1 instrucción por ciclo"""
    
    def __init__(self):
        super().__init__("Uniciclo")
        self.clock_period = 30  # ns - período determinado por la instrucción más lenta
    
    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        self.total_cycles = self.total_instructions  # 1 ciclo por instrucción
        
        # Tiempo total = ciclos × período de reloj
        execution_time = self.total_cycles * self.clock_period
        
        return {
            'architecture': self.name,
            'total_cycles': self.total_cycles,
            'total_instructions': self.total_instructions,
            'clock_period_ns': self.clock_period,
            'execution_time_ns': execution_time,
            'frequency_mhz': 1000 / self.clock_period,
            'ipc': 1.0,
            'throughput_mips': (self.total_instructions / execution_time) * 1000
        }

class PipelineArch(Architecture):
    """Arquitectura Pipeline - 5 etapas"""
    
    def __init__(self):
        super().__init__("Pipeline")
        self.stages = 5
        self.clock_period = 8  # ns - período más corto por etapa
        self.hazard_penalty = 2  # ciclos de penalización por hazard
    
    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        
        # Calcular hazards
        data_hazards = self._count_data_hazards(tea_code.instructions)
        branch_hazards = self._count_branch_hazards(tea_code.instructions)
        
        # Ciclos = instrucciones + (stages-1) + penalizaciones
        pipeline_fill = self.stages - 1
        hazard_cycles = (data_hazards + branch_hazards) * self.hazard_penalty
        self.total_cycles = self.total_instructions + pipeline_fill + hazard_cycles
        
        execution_time = self.total_cycles * self.clock_period
        
        return {
            'architecture': self.name,
            'total_cycles': self.total_cycles,
            'total_instructions': self.total_instructions,
            'clock_period_ns': self.clock_period,
            'execution_time_ns': execution_time,
            'frequency_mhz': 1000 / self.clock_period,
            'ipc': self.total_instructions / self.total_cycles,
            'throughput_mips': (self.total_instructions / execution_time) * 1000,
            'data_hazards': data_hazards,
            'branch_hazards': branch_hazards,
            'hazard_penalty_cycles': hazard_cycles
        }
    
    def _count_data_hazards(self, instructions: List[Instruction]) -> int:
        hazards = 0
        for i in range(1, len(instructions)):
            # Simulación simple: 30% de probabilidad de hazard de datos
            if instructions[i].arithmetic and instructions[i-1].arithmetic:
                hazards += 0.3
        return int(hazards)
    
    def _count_branch_hazards(self, instructions: List[Instruction]) -> int:
        return sum(1 for inst in instructions if inst.branch)

class VLIWArch(Architecture):
    """Arquitectura VLIW con múltiples unidades funcionales"""
    
    def __init__(self):
        super().__init__("VLIW")
        # Unidades funcionales disponibles (pueden duplicarse)
        self.functional_units = {
            'alu1': {'type': 'alu', 'available': True},
            'alu2': {'type': 'alu', 'available': True},  # ALU duplicada
            'memory1': {'type': 'memory', 'available': True},
            'memory2': {'type': 'memory', 'available': True},  # Load/Store duplicada
            'branch': {'type': 'branch', 'available': True},
            'multiplier': {'type': 'mult', 'available': True},
            'specialized': {'type': 'specialized', 'available': True}  # Espacio para FU especializada
        }
        self.max_issue_width = len(self.functional_units)
        self.clock_period = 10  # ns
    
    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        
        # Agrupar instrucciones en paquetes VLIW
        vliw_packets = self._create_vliw_packets(tea_code.instructions)
        self.total_cycles = len(vliw_packets)
        
        execution_time = self.total_cycles * self.clock_period
        
        return {
            'architecture': self.name,
            'total_cycles': self.total_cycles,
            'total_instructions': self.total_instructions,
            'clock_period_ns': self.clock_period,
            'execution_time_ns': execution_time,
            'frequency_mhz': 1000 / self.clock_period,
            'ipc': self.total_instructions / self.total_cycles,
            'throughput_mips': (self.total_instructions / execution_time) * 1000,
            'vliw_packets': len(vliw_packets),
            'avg_instructions_per_packet': self.total_instructions / len(vliw_packets),
            'functional_units': len(self.functional_units)
        }
    
    def _create_vliw_packets(self, instructions: List[Instruction]) -> List[List[Instruction]]:
        packets = []
        current_packet = []
        
        i = 0
        while i < len(instructions):
            # Reiniciar disponibilidad de unidades funcionales
            self._reset_functional_units()
            current_packet = []
            
            # Intentar agrupar tantas instrucciones como sea posible en este ciclo
            while i < len(instructions) and len(current_packet) < self.max_issue_width:
                inst = instructions[i]
                required_unit_type = self._get_required_unit_type(inst)
                
                # Buscar una unidad funcional disponible del tipo requerido
                available_unit = self._find_available_unit(required_unit_type)
                
                if available_unit:
                    current_packet.append(inst)
                    self.functional_units[available_unit]['available'] = False
                    i += 1
                else:
                    # No hay unidad disponible, pasar al siguiente ciclo
                    break
            
            if current_packet:
                packets.append(current_packet)
            
            # Si no se pudo emitir ninguna instrucción, forzar avance
            if not current_packet and i < len(instructions):
                packets.append([instructions[i]])
                i += 1
        
        return packets
    
    def _reset_functional_units(self):
        """Reinicia la disponibilidad de todas las unidades funcionales"""
        for unit in self.functional_units.values():
            unit['available'] = True
    
    def _find_available_unit(self, unit_type: str) -> str:
        """Encuentra una unidad funcional disponible del tipo especificado"""
        for unit_name, unit_info in self.functional_units.items():
            if unit_info['type'] == unit_type and unit_info['available']:
                return unit_name
        return None
    
    def _get_required_unit_type(self, inst: Instruction) -> str:
        """Determina qué tipo de unidad funcional requiere la instrucción"""
        if inst.memory_access:
            return 'memory'
        elif inst.branch:
            return 'branch'
        elif inst.type == InstructionType.MUL:
            return 'mult'
        elif inst.type == InstructionType.SAXS:
            return 'specialized'  # SAXS puede usar la unidad especializada
        else:
            return 'alu'

@dataclass
class ReservationStation:
    """Estación de reserva para algoritmo de Tomasulo"""
    name: str
    busy: bool = False
    op: str = ""
    vj: str = ""  # Valor o tag del operando j
    vk: str = ""  # Valor o tag del operando k
    qj: str = ""  # Tag del productor del operando j
    qk: str = ""  # Tag del productor del operando k
    dest: str = ""  # Registro destino
    cycles_remaining: int = 0

@dataclass
class RegisterStatus:
    """Estado de los registros para Tomasulo"""
    qi: str = ""  # Tag de la unidad funcional que producirá el valor

class SuperescalarArch(Architecture):
    """Arquitectura Superescalar basada en algoritmo de Tomasulo"""
    
    def __init__(self):
        super().__init__("Superescalar")
        self.issue_width = 2  # instrucciones por ciclo
        self.clock_period = 6  # ns
        
        # Mismas unidades funcionales que VLIW
        self.reservation_stations = {
            'alu1': ReservationStation('alu1'),
            'alu2': ReservationStation('alu2'),
            'memory1': ReservationStation('memory1'),
            'memory2': ReservationStation('memory2'),
            'branch': ReservationStation('branch'),
            'multiplier': ReservationStation('multiplier'),
            'specialized': ReservationStation('specialized')  # Para SAXS
        }
        
        # Latencias de ejecución por tipo de unidad
        self.execution_latencies = {
            'alu1': 1, 'alu2': 1,
            'memory1': 3, 'memory2': 3,
            'branch': 1,
            'multiplier': 4,
            'specialized': 2  # Para SAXS
        }
        
        # Estado de registros (simplificado con algunos registros clave)
        self.register_status = {f'R{i}': RegisterStatus() for i in range(16)}
    
    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        
        # Simular ejecución con Tomasulo
        cycles_needed = self._simulate_tomasulo(tea_code.instructions)
        self.total_cycles = cycles_needed
        
        execution_time = self.total_cycles * self.clock_period
        
        return {
            'architecture': self.name,
            'total_cycles': self.total_cycles,
            'total_instructions': self.total_instructions,
            'clock_period_ns': self.clock_period,
            'execution_time_ns': execution_time,
            'frequency_mhz': 1000 / self.clock_period,
            'ipc': self.total_instructions / self.total_cycles,
            'throughput_mips': (self.total_instructions / execution_time) * 1000,
            'issue_width': self.issue_width,
            'reservation_stations': len(self.reservation_stations)
        }
    
    def _simulate_tomasulo(self, instructions: List[Instruction]) -> int:
        """Simula la ejecución usando el algoritmo de Tomasulo"""
        cycle = 0
        instruction_queue = instructions.copy()
        issued_instructions = []
        completed_instructions = 0
        
        while completed_instructions < len(instructions):
            cycle += 1
            
            # 1. Write Back - completar instrucciones que terminaron ejecución
            self._writeback_phase()
            
            # 2. Execute - decrementar ciclos de instrucciones en ejecución
            completed_this_cycle = self._execute_phase()
            completed_instructions += completed_this_cycle
            
            # 3. Issue - emitir nuevas instrucciones si hay estaciones disponibles
            if instruction_queue:
                self._issue_phase(instruction_queue)
        
        return cycle
    
    def _issue_phase(self, instruction_queue: List[Instruction]):
        """Fase de emisión - intenta emitir hasta issue_width instrucciones"""
        issued_count = 0
        
        while issued_count < self.issue_width and instruction_queue:
            inst = instruction_queue[0]
            required_unit_type = self._get_required_unit_type(inst)
            
            # Buscar estación de reserva disponible
            available_station = self._find_available_station(required_unit_type)
            
            if available_station:
                # Emitir instrucción
                self._issue_instruction(inst, available_station)
                instruction_queue.pop(0)
                issued_count += 1
            else:
                # No hay estaciones disponibles, esperar
                break
    
    def _execute_phase(self) -> int:
        """Fase de ejecución - decrementar ciclos y marcar completadas"""
        completed = 0
        
        for station in self.reservation_stations.values():
            if station.busy and station.cycles_remaining > 0:
                station.cycles_remaining -= 1
                if station.cycles_remaining == 0:
                    completed += 1
        
        return completed
    
    def _writeback_phase(self):
        """Fase de write-back - liberar estaciones completadas"""
        for station in self.reservation_stations.values():
            if station.busy and station.cycles_remaining == 0:
                # Liberar estación de reserva
                station.busy = False
                station.op = ""
                station.dest = ""
                # Actualizar estado de registros (simplificado)
                if station.dest:
                    self.register_status[station.dest].qi = ""
    
    def _issue_instruction(self, inst: Instruction, station_name: str):
        """Emite una instrucción a una estación de reserva"""
        station = self.reservation_stations[station_name]
        station.busy = True
        station.op = inst.type.value
        station.cycles_remaining = self.execution_latencies[station_name]
        
        # Simplificación: asignar destino si es una instrucción que escribe
        if len(inst.operands) > 0 and inst.operands[0].startswith('R'):
            station.dest = inst.operands[0]
            self.register_status[station.dest].qi = station_name
    
    def _find_available_station(self, unit_type: str) -> str:
        """Encuentra una estación de reserva disponible del tipo requerido"""
        for station_name, station in self.reservation_stations.items():
            if not station.busy:
                # Verificar si el tipo de estación coincide
                if ((unit_type == 'alu' and station_name.startswith('alu')) or
                    (unit_type == 'memory' and station_name.startswith('memory')) or
                    (unit_type == 'branch' and station_name == 'branch') or
                    (unit_type == 'mult' and station_name == 'multiplier') or
                    (unit_type == 'specialized' and station_name == 'specialized')):
                    return station_name
        return None
    
    def _get_required_unit_type(self, inst: Instruction) -> str:
        """Determina qué tipo de unidad funcional requiere la instrucción"""
        if inst.memory_access:
            return 'memory'
        elif inst.branch:
            return 'branch'
        elif inst.type == InstructionType.MUL:
            return 'mult'
        elif inst.type == InstructionType.SAXS:
            return 'specialized'  # SAXS usa la unidad especializada
        else:
            return 'alu'
        
class SuperescalarMarcadorArch(Architecture):
    """Arquitectura Superescalar basada en algoritmo Marcador"""
    
    def __init__(self):
        super().__init__("Superescalar-Marcador")
        self.issue_width = 2  # instrucciones por ciclo
        self.clock_period = 6  # ns

    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        
        # Simulación básica: emite hasta 2 instrucciones por ciclo, sin reordenamiento ni ejecución especulativa
        instructions = tea_code.instructions
        cycles = 0
        issued = 0
        
        while issued < len(instructions):
            issue_count = 0
            while issue_count < self.issue_width and issued < len(instructions):
                # Supone que todas las instrucciones están listas para emitirse (no se evalúa dependencias)
                issue_count += 1
                issued += 1
            cycles += 1  # un ciclo por grupo de emisión
        
        self.total_cycles = cycles
        execution_time = self.total_cycles * self.clock_period

        return {
            'architecture': self.name,
            'total_cycles': self.total_cycles,
            'total_instructions': self.total_instructions,
            'clock_period_ns': self.clock_period,
            'execution_time_ns': execution_time,
            'frequency_mhz': 1000 / self.clock_period,
            'ipc': self.total_instructions / self.total_cycles,
            'throughput_mips': (self.total_instructions / execution_time) * 1000,
            'issue_width': self.issue_width
        }


class MulticicloArch(Architecture):
    """Arquitectura Multiciclo - diferentes instrucciones toman diferentes ciclos"""
    
    def __init__(self):
        super().__init__("Multiciclo")
        self.clock_period = 5  # ns - período corto
        self.instruction_cycles = {
            InstructionType.LOAD: 5,
            InstructionType.STOR: 4,
            InstructionType.DLT: 3,
            InstructionType.SAXS: 3,
            InstructionType.ADD: 1,
            InstructionType.SUB: 1,
            InstructionType.MUL: 4,
            InstructionType.XOR: 1,
            InstructionType.LOOP: 3
        }
    
    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        
        # Calcular ciclos totales
        self.total_cycles = sum(
            self.instruction_cycles.get(inst.type, 2) 
            for inst in tea_code.instructions
        )
        
        execution_time = self.total_cycles * self.clock_period
        
        return {
            'architecture': self.name,
            'total_cycles': self.total_cycles,
            'total_instructions': self.total_instructions,
            'clock_period_ns': self.clock_period,
            'execution_time_ns': execution_time,
            'frequency_mhz': 1000 / self.clock_period,
            'ipc': self.total_instructions / self.total_cycles,
            'throughput_mips': (self.total_instructions / execution_time) * 1000
        }

class TEAAnalyzer:
    """Analizador principal que coordina todas las arquitecturas"""
    
    def __init__(self):
        self.architectures = [
            UnicicloArch(),
            PipelineArch(),
            VLIWArch(),
            SuperescalarArch(),
            SuperescalarMarcadorArch()
        ]
        self.tea_code = TEACode()
        self.results = []
    
    def run_analysis(self):
        """Ejecuta el análisis en todas las arquitecturas"""
        print("🔄 Ejecutando análisis del algoritmo TEA...")
        print(f"📊 Total de instrucciones: {len(self.tea_code.instructions)}")
        print("=" * 60)
        
        for arch in self.architectures:
            print(f"⚡ Analizando arquitectura: {arch.name}")
            result = arch.analyze(self.tea_code)
            self.results.append(result)
            
            # Mostrar resultados inmediatos
            print(f"   ⏰ Tiempo de ejecución: {result['execution_time_ns']:.0f} ns")
            print(f"   🔄 Ciclos totales: {result['total_cycles']}")
            print(f"   📈 IPC: {result['ipc']:.2f}")
            print(f"   🚀 Throughput: {result['throughput_mips']:.1f} MIPS")
            print()
    
    def generate_comparison_table(self):
        """Genera tabla comparativa de resultados"""
        df = pd.DataFrame(self.results)
        
        # Ordenar por tiempo de ejecución (mejor primero)
        df_sorted = df.sort_values('execution_time_ns')
        
        print("\n📋 TABLA COMPARATIVA DE RENDIMIENTO")
        print("=" * 80)
        
        columns = ['architecture', 'execution_time_ns', 'total_cycles', 'frequency_mhz', 'ipc', 'throughput_mips']
        print(f"{'Arquitectura':<12} {'Tiempo(ns)':<12} {'Ciclos':<8} {'Freq(MHz)':<10} {'IPC':<6} {'MIPS':<8}")
        print("-" * 80)
        
        for _, row in df_sorted.iterrows():
            print(f"{row['architecture']:<12} {row['execution_time_ns']:<12.0f} "
                  f"{row['total_cycles']:<8} {row['frequency_mhz']:<10.1f} "
                  f"{row['ipc']:<6.2f} {row['throughput_mips']:<8.1f}")
    
    def generate_performance_chart(self):
        """Genera gráfico de comparación de rendimiento"""
        architectures = [r['architecture'] for r in self.results]
        execution_times = [r['execution_time_ns'] for r in self.results]
        throughputs = [r['throughput_mips'] for r in self.results]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico de tiempo de ejecución
        bars1 = ax1.bar(architectures, execution_times, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        ax1.set_title('Tiempo de Ejecución por Arquitectura', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Tiempo (ns)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar, value in zip(bars1, execution_times):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico de throughput
        bars2 = ax2.bar(architectures, throughputs, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        ax2.set_title('Throughput por Arquitectura', fontsize=14, fontweight='bold')
        ax2.set_ylabel('MIPS')
        ax2.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar, value in zip(bars2, throughputs):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def generate_detailed_report(self):
        """Genera reporte detallado con métricas adicionales"""
        print("\n📄 REPORTE DETALLADO DE ANÁLISIS")
        print("=" * 60)
        
        fastest = min(self.results, key=lambda x: x['execution_time_ns'])
        highest_throughput = max(self.results, key=lambda x: x['throughput_mips'])
        best_ipc = max(self.results, key=lambda x: x['ipc'])
        
        print(f"🏆 Arquitectura más rápida: {fastest['architecture']} ({fastest['execution_time_ns']:.0f} ns)")
        print(f"🚀 Mayor throughput: {highest_throughput['architecture']} ({highest_throughput['throughput_mips']:.1f} MIPS)")
        print(f"⚡ Mejor IPC: {best_ipc['architecture']} ({best_ipc['ipc']:.2f})")
        
        print(f"\n📊 Mejoras relativas respecto a Uniciclo:")
        uniciclo_time = next(r['execution_time_ns'] for r in self.results if r['architecture'] == 'Uniciclo')
        
        for result in self.results:
            if result['architecture'] != 'Uniciclo':
                speedup = uniciclo_time / result['execution_time_ns']
                print(f"   {result['architecture']}: {speedup:.2f}x más rápido")

def main():
    """Función principal"""
    print("🔬 ANALIZADOR DE RENDIMIENTO - ALGORITMO TEA")
    print("Comparación de Microarquitecturas: Uniciclo, Pipeline, VLIW, Superescalar")
    print("=" * 80)
    
    # Crear y ejecutar analizador
    analyzer = TEAAnalyzer()
    analyzer.run_analysis()
    analyzer.generate_comparison_table()
    analyzer.generate_detailed_report()
    
    # Generar gráficos
    try:
        analyzer.generate_performance_chart()
    except ImportError:
        print("\n⚠️  matplotlib no disponible - omitiendo gráficos")
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":main()