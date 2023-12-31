from .tui_interface import DebuggerTUI, Info, HexDumpLine, CodeLine, CodeScroll
from ..machine import Machine, Opcode, Register, TrapType
from ..disassembler import Disassembler
from ..utils import *
from typing import List

class Debugger:

    tui: DebuggerTUI
    machine: Machine
    disassembler: Disassembler

    #scroll effect: 0= disabled, 1= follow jumps, 2 follow cursor
    scroll_effect = 1
    previous_line = 0

    #machine snapshots for time travel
    vmem_snapshots = []
    current_snapshot = 0
    # program_exit = False
    trap_reached: None|TrapType = None

    breaks: List[int] = []
    continue_until_break = False

    def __init__(self, machine: Machine, breaks, comments={}):
        #init machine
        self.machine = machine
        self.machine.trap_mode_enabled = True
        def handler(_, type):
            self.trap_handler(type)
        self.machine.set_trap_handler(handler)

        #init disassembler
        self.disassembler = Disassembler(machine, comments=comments)

        #init debugger
        self.breaks = breaks

        # init TUI
        self.tui = DebuggerTUI()
        self.tui.continue_callback = self.continue_callback
        self.tui.stepi_callback = self.stepi_callback
        self.tui.reverse_stepi_callback = self.reverse_stepi_callback
        self.tui.context_callback = self.context_callback
        self.tui.ready_callback = self.ready_callback
        
        # launch the TUI
        self.tui.run()


    def trap_handler(self, type: TrapType):
        # we reached a trap
        if type is not TrapType.trap_mode:
            self.trap_reached = type
            self.continue_until_break = False
            self.print(f"Reached unhandled trap: {type.value}")
            self.update_hexdump()
            self.update_code()
        # we are single stepping peacefully
        elif not self.continue_until_break:
            self.update_info()
            self.update_hexdump()
            self.update_code()
        # c was pressed, we reached a breakpoint
        elif self.is_breakpoint():
            self.continue_until_break = False
            self.print("Reached breakpoint")
            self.update_hexdump()
            self.update_code()
        # c was pressed, we didn't reach a breakpoint yet
        else:
            self.stepi_callback()


    def is_breakpoint(self)-> bool:
        i = self.machine._read_register(Register.i)
        instruction_addr = i*3
        return instruction_addr in self.breaks


    def update_info(self):
        register_f_bytes = self.machine._read_register(Register.f)
        flags = [f.value for f in self.machine._get_flags(register_f_bytes)]
        flags = "".join(flags)
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
        reg = self.machine._read_register(Register.s)
        res += f"{RESET_COLOR}s{RESET_COLOR}:{hex(reg)}  "
        reg = self.machine._read_register(Register.f)
        res += f"f:{hex(reg)} ({flags}) "
        res += "       (s: step   r: reverse step   ctrl+c: quit)"
        self.tui.query_one(Info).txt = res
    
    def print(self, msg, help=" (x to print context)"):
        self.tui.query_one(Info).txt = msg + help

    def update_code(self):
        txt = self.disassembler.disassemble()
        self.tui.query_one(CodeLine).txt = txt

        # scroll
        line = self.machine._read_register(Register.i)
        sub = 2
        if sub > line:
            sub = 0

        # scroll effect 1: follow jumps
        # scroll only when there is a jump
        if self.scroll_effect == 1:
            scroll = False
            if self.previous_line is None:
                scroll = True
            elif abs(line - self.previous_line) > 4:
                scroll = True
            if scroll:
                self.tui.query_one(CodeScroll).scroll_to(y=line-sub, speed=300)
            self.previous_line = line

        # scroll effect 2: follow cursor
        # keep the cursor on top
        elif self.scroll_effect == 2:
            self.tui.query_one(CodeScroll).scroll_to(y=line-sub, speed=800)

    def update_hexdump(self):
        stack_address =self.machine._read_register(Register.s) + self.machine.conf_memory_base_address
        self.tui.query_one(HexDumpLine).data = self.machine.vmem[::]
        self.tui.query_one(HexDumpLine).stack_address = stack_address


    def ready_callback(self):
        self.update_hexdump()
        self.update_code()

    def continue_callback(self):
        self.continue_until_break = True
        self.stepi_callback()


    def stepi_callback(self):
        if self.trap_reached is not None:
            self.print(f"Reached unhandled trap: {self.trap_reached.value}")
        else:
            #record a snapshot ot the current machine state
            self.vmem_snapshots.append(self.machine.vmem[::])
            # run the machine
            self.machine.run_loop()

    def reverse_stepi_callback(self):
        #restore previous machine state
        if len(self.vmem_snapshots) > 0:
            self.trap_reached = None
            vmem = self.vmem_snapshots.pop()
            self.machine.vmem = vmem[::]
            # we pretend the machine executed, and called the trap handler
            self.trap_handler(TrapType.trap_mode)
        else:
            self.print(f"Reached end of the recording")

    def context_callback(self):
        self.update_info()

