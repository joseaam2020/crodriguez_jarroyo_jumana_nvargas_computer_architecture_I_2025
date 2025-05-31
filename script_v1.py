#!/usr/bin/env python3
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
    """Arquitectura VLIW - 4 unidades de ejecución"""
    
    def __init__(self):
        super().__init__("VLIW")
        self.execution_units = 4  # ALU, Load/Store, Branch, Multiplier
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
            'avg_instructions_per_packet': self.total_instructions / len(vliw_packets)
        }
    
    def _create_vliw_packets(self, instructions: List[Instruction]) -> List[List[Instruction]]:
        packets = []
        current_packet = []
        unit_usage = {'alu': False, 'memory': False, 'branch': False, 'mult': False}
        
        for inst in instructions:
            required_unit = self._get_required_unit(inst)
            
            # Si la unidad ya está ocupada o el paquete está lleno, crear nuevo paquete
            if unit_usage[required_unit] or len(current_packet) >= self.execution_units:
                packets.append(current_packet)
                current_packet = []
                unit_usage = {'alu': False, 'memory': False, 'branch': False, 'mult': False}
            
            current_packet.append(inst)
            unit_usage[required_unit] = True
        
        if current_packet:
            packets.append(current_packet)
        
        return packets
    
    def _get_required_unit(self, inst: Instruction) -> str:
        if inst.memory_access:
            return 'memory'
        elif inst.branch:
            return 'branch'
        elif inst.type == InstructionType.MUL:
            return 'mult'
        else:
            return 'alu'

class SuperescalarArch(Architecture):
    """Arquitectura Superescalar - 2 instrucciones por ciclo"""
    
    def __init__(self):
        super().__init__("Superescalar")
        self.issue_width = 2  # instrucciones por ciclo
        self.clock_period = 6  # ns
    
    def analyze(self, tea_code: TEACode) -> Dict:
        self.total_instructions = len(tea_code.instructions)
        
        # Calcular ciclos considerando dependencias
        cycles_needed = self._calculate_superescalar_cycles(tea_code.instructions)
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
            'issue_width': self.issue_width
        }
    
    def _calculate_superescalar_cycles(self, instructions: List[Instruction]) -> int:
        cycles = 0
        i = 0
        
        while i < len(instructions):
            issued_this_cycle = 0
            
            # Intentar emitir hasta 2 instrucciones por ciclo
            while issued_this_cycle < self.issue_width and i < len(instructions):
                # Verificar dependencias (simplificado)
                if self._can_issue_parallel(instructions, i, issued_this_cycle):
                    issued_this_cycle += 1
                    i += 1
                else:
                    break
            
            cycles += 1
            
            # Si no se pudo emitir ninguna instrucción, forzar avance
            if issued_this_cycle == 0:
                i += 1
        
        return cycles
    
    def _can_issue_parallel(self, instructions: List[Instruction], index: int, already_issued: int) -> bool:
        # Simplificación: no emitir dos instrucciones de memoria en paralelo
        if already_issued > 0 and instructions[index].memory_access:
            return False
        return True

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
            MulticicloArch()
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
        bars1 = ax1.bar(architectures, execution_times, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax1.set_title('Tiempo de Ejecución por Arquitectura', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Tiempo (ns)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar, value in zip(bars1, execution_times):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico de throughput
        bars2 = ax2.bar(architectures, throughputs, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
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
    print("Comparación de Microarquitecturas: Uniciclo, Pipeline, VLIW, Superescalar, Multiciclo")
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