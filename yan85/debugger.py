from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Button, Footer, Header, Static
from textual.reactive import reactive
from utils import *

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


class Debugger(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("s", "stepi", "step instruction")]
    CSS_PATH = "debugger_styles.tcss"

    count = 0
    info_text = reactive("i: 0x12 (i*3 = 0x322)  A=0x1 B C D s f ")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Info(self.info_text)
        yield Columns()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_stepi(self) -> None:
        self.count += 1
        self.info_text = f"{self.count}"
        pass


if __name__ == "__main__":
    app = Debugger()
    app.run()
