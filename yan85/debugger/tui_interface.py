from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Button, Footer, Header, Static
from textual.reactive import reactive
from ..utils import *
from typing import Callable
from rich.text import Text

class HexDumpLine(Static):
    """print a hexdump from the data list. if the data is updated, the hexdump will update"""
    data = reactive([0]*1500) #add layout=True to fir for future data size changes

    stack_address = reactive(0)

    def generate_hexdump(self):
        current_address = 0
        data = self.data
        pad = "    "
        ret = ""
        for i in range(0, len(data), 16):
            hex_vals = []
            ascii_vals = []
            for j in range(i, min(i + 16, len(data))):
                val = data[j]
                if current_address == self.stack_address:
                    color = INVERT
                elif val == 0:
                    color = DARK_GRAY
                else:
                    color = RESET_COLOR
                current_address += 1

                hex_vals.append(f"{color}{val:02X}{RESET_COLOR}")
                ascii_vals.append(chr(val) if ord(' ') <= val <= ord('~') else ".")

            hex_padding = ""
            if(len(hex_vals) < 16):
                hex_padding = " __" * (16 - len(hex_vals))

            ret += f"{i:04X}" + pad
            ret += " ".join(hex_vals) + hex_padding + pad
            ret += "".join(ascii_vals) + "\n"
        return Text.from_ansi(ret)

    def render(self)->Text:
        return self.generate_hexdump()


class CodeLine(Static):
    """todo"""
    default = """
 ______________________
(0RGSDOFCJftli;:.:. .  )
 T====================T
 |.;....,..........;..|
 |;;:: .  .    .      |
 l;;;:. :   .     ..  ;
 `;;:::.: .    .     .'
  l;;:. ..  .     .: ;
  `;;::.. .    .  ; .'
   l;;:: .  .    /  ;
    \\;;:. .   .,'  /
     `\\;:.. ..'  .'
       `\\;:.. ..'
         \\;:. /
          l; f
          `;f'
           ||
           ;l.
          ;: l
         / ;  \\
       ,/  :   `.
     ./' . :     `.
    /' ,'  :       \\
   f  /  . :        i
  ,' ;  .  :        `.
  f ;  .   :      .  i
 .'    :   :       . `.
 f ,  .    ;       :  i
 |    :  ,/`.       : |
 |    ;,/;:. `.     . |
 |___,/;;:. . .`._____|
(QB0ZDOLC7itz!;:.:. .  )
 =====================-
"""
    txt = reactive(default + ".\n"*350)
    def render(self)->Text:
        return Text.from_ansi(self.txt)


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


class CodeScroll(ScrollableContainer):
    """"""

class Code(Static):
    DEFAULT_CSS = """
    Code {
      layout: vertical;
      width: 70;
      dock: right;
    }
    """
    def compose(self) -> ComposeResult:
        yield CodeScroll(CodeLine())


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

    txt = reactive("Debugger ready.   s: step   r: reverse step   c: continue   x: context")

    def render(self)->Text:
        return Text.from_ansi(" " + self.txt)



class DebuggerTUI(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("s", "stepi", "step instruction"),
                ("r", "reverse_stepi", "step one instruction back in time"),
                ("x", "context", "print context"),
                ("c", "continue", "continue until break"),
                ]
    CSS_PATH = "styles.tcss"

    count = 0
    continue_callback: None|Callable = None
    stepi_callback: None|Callable = None
    reverse_stepi_callback: None|Callable = None
    context_callback: None|Callable = None
    ready_callback: None|Callable = None


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Info()
        yield Columns()

    def on_ready(self) -> None:
        if self.ready_callback is not None:
            self.ready_callback()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_continue(self) -> None:
        """continue to next breakpoint"""
        if self.continue_callback is not None:
            self.continue_callback()

    def action_stepi(self) -> None:
        """step instruction"""
        if self.stepi_callback is not None:
            self.stepi_callback()

    def action_reverse_stepi(self) -> None:
        """reverse step instruction"""
        if self.reverse_stepi_callback is not None:
            self.reverse_stepi_callback()

    def action_context(self) -> None:
        """print context"""
        if self.context_callback is not None:
            self.context_callback()

