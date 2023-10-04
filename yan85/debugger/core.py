from .tui_interface import DebuggerTUI, Info
from ..machine import Machine, Opcode, Register, TrapType
from ..disassembler import Disassembler

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
        # self.disassembler = Disassembler(machine)

        # init TUI
        self.tui = DebuggerTUI()
        self.tui.stepi_callback = self.stepi_callback

        # launch the TUI
        self.tui.run()


    def trap_handler(self, type: TrapType):
            if type is not TrapType.trap_mode:
                print(f"some actual error occurred {type}")
            else:
                # update info
                reg = self.machine._read_register(Register.i)
                self.tui.query_one(Info).txt = f"i: {hex(reg)}"

    def update_info(self):
        pass

    def update_code(self):
        pass

    def update_hexdump(self):
        pass

    def stepi_callback(self):
        self.machine.run_loop()

