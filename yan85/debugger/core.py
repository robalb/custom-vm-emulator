from .tui_interface import DebuggerTUI, Info, HexDumpLine, CodeLine
from ..machine import Machine, Opcode, Register, TrapType
from ..disassembler import Disassembler
# from ..utils import hexdump

class Debugger:

    tui: DebuggerTUI
    machine: Machine
    disassembler: Disassembler

    def __init__(self, machine: Machine):
        #init machine
        self.machine = machine
        self.machine.trap_mode_enabled = True
        def handler(_, type):
            self.trap_handler(type)
        self.machine.set_trap_handler(handler)

        #init disassembler
        self.disassembler = Disassembler(machine)

        # init TUI
        self.tui = DebuggerTUI()
        self.tui.stepi_callback = self.stepi_callback
        self.tui.context_callback = self.context_callback
        self.tui.ready_callback = self.ready_callback
        
        # launch the TUI
        self.tui.run()


    def trap_handler(self, type: TrapType):
            if type is not TrapType.trap_mode:
                self.print(f" Error: {type.value} (c to print context)")
            else:
                self.update_info()
            self.update_hexdump()
            self.update_code()

    def update_info(self):
        res = ""
        reg = self.machine._read_register(Register.i)
        res += f"i:{hex(reg)}  i*3:{hex(reg*3)}  "

        reg = self.machine._read_register(Register.A)
        res += f"A:{hex(reg)}  "
        reg = self.machine._read_register(Register.B)
        res += f"B:{hex(reg)}  "
        reg = self.machine._read_register(Register.C)
        res += f"C:{hex(reg)}  "
        reg = self.machine._read_register(Register.D)
        res += f"D:{hex(reg)}  "
        reg = self.machine._read_register(Register.f)
        res += f"f:{hex(reg)}  "
        reg = self.machine._read_register(Register.s)
        res += f"s:{hex(reg)}  "
        res += "       (s: step   r: reverse step   ctrl+c: quit)"
        self.tui.query_one(Info).txt = res
    
    def print(self, msg):
        self.tui.query_one(Info).txt = msg

    def update_code(self):

        txt = self.disassembler.disassemble()
        self.tui.query_one(CodeLine).txt = txt

    def update_hexdump(self):
        self.tui.query_one(HexDumpLine).data = self.machine.vmem[::]

    def ready_callback(self):
        self.update_hexdump()
        self.update_code()

    def stepi_callback(self):
        self.machine.run_loop()

    def context_callback(self):
        self.update_info()

