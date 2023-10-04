from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Button, Footer, Header, Static
from textual.reactive import reactive
from ..utils import *
from typing import Callable

class HexDumpLine(Static):
    """todo"""

class CodeLine(Static):
    """todo"""


class HexDump(Static):
    DEFAULT_CSS = """
    HexDump {
      layout: vertical;
      width: 80;
      dock: left;
    }
    """
    def compose(self) -> ComposeResult:
        list = [
            HexDumpLine(
                    f"{i} 0170    00 40 02 85 08 02 08 40 10 80 40 20 00 80 20 08    .@.....@..@ .. ."
                    ) for i in range(100)
            ]
        yield ScrollableContainer(*list)

class Code(Static):
    DEFAULT_CSS = """
    Code {
      layout: vertical;
      width: 70;
      dock: right;
    }
    """

    def compose(self) -> ComposeResult:
        list = [
            CodeLine(
            f"{i}|| /--- 01CE  04 18 08  ??    04 24 08     JMP Invalid Register",
            ) for i in range(80)
                ]
        yield ScrollableContainer(*list)


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
    """aaa"""

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
    reverse_stepi_callback = None
    context_callback = None


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
        pass

