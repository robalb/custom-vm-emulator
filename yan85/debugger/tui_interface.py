from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Button, Footer, Header, Static
from textual.reactive import reactive
from ..utils import *
from typing import Callable
from rich.text import Text

class HexDumpLine(Static):
    """todo"""
    data = reactive([0]*1500)

    def generate_hexdump(self):
        data = self.data
        pad = "    "
        ret = Text()
        for i in range(0, len(data), 16):
            hex_vals = []
            ascii_vals = []

            for j in range(i, min(i + 16, len(data))):
                val = data[j]
                if val == 0:
                    hex_vals.append(Text("..", style="gray"))
                else:
                    hex_vals.append(f"{val:02X}")
                ascii_vals.append(chr(val) if ord(' ') <= val <= ord('~') else ".")

            hex_padding = ""
            if(len(hex_vals) < 16):
                hex_padding = " __" * (16 - len(hex_vals))

            ret.append(f"{i:04X}{pad}")
            ret.append(Text("..", style="red"))
            # ret.append(Text.assemble(
            #         f"{i:04X}{pad}",
            #         (" ".join(hex_vals) + hex_padding + pad),
            #         ("".join(ascii_vals)),
            #         "\n",
            #         ))
        return Text("..", style="red")

    def render(self)->Text:
        return self.generate_hexdump()


class CodeLine(Static):
    """todo"""
    txt = reactive([0]*150)

    def process_data(self):
        arr = [f"{d}\n" for d in self.txt]
        return " ".join(arr)

    def render(self)->str:
        return self.process_data()


class HexDump(Static):
    DEFAULT_CSS = """
    HexDump {
      layout: vertical;
      width: 80;
      dock: left;
    }
    """

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
                HexDumpLine())


class Code(Static):
    DEFAULT_CSS = """
    Code {
      layout: vertical;
      width: 70;
      dock: right;
    }
    """
    def compose(self) -> ComposeResult:
        yield ScrollableContainer(CodeLine())


class Columns(Static):
    DEFAULT_CSS = """
    Columns {
      layout: horizontal;
      min-height: 20;
      min-width: 70;
    }
    """
    def compose(self) -> ComposeResult:
        yield HexDump()
        yield Code()


class Info(Static):
    DEFAULT_CSS = """
    Info {
        dock: bottom;
        width: 100%;
        background: $foreground 5%;
        color: $text;
        height: 3;
        border: round white;
    }
    """

    txt = reactive("Debugger ready.   s: step   c: context   r: reverse step")

    def render(self)->str:
        return f" {self.txt}"



class DebuggerTUI(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("s", "stepi", "step instruction"),
                ("r", "reverse_stepi", "step one instruction back in time"),
                ("c", "context", "print context"),
                ]
    CSS_PATH = "styles.tcss"

    count = 0
    stepi_callback: None|Callable = None
    reverse_stepi_callback: None|Callable = None
    context_callback: None|Callable = None


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Info()
        yield Columns()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_stepi(self) -> None:
        """step instruction"""
        if self.stepi_callback is not None:
            self.stepi_callback()
        # self.count += 1
        # self.query_one(Info).txt = f"{self.count}"

    def action_reverse_stepi(self) -> None:
        """reverse step instruction"""
        pass

    def action_context(self) -> None:
        """print context"""
        if self.context_callback is not None:
            self.context_callback()

