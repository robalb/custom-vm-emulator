# ANSI escape codes for text colors
RESET_COLOR = "\033[0m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
LIGHT_GRAY = "\033[37m"
DARK_GRAY = "\033[90m"
EXTRA_DARK_GRAY = "\033[2m"


BLUE_COMMENT = "\033[38;5;210m"
BLUE_COMMENT = "\033[38;5;177m"

# ANSI escape codes for text styles
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
INVERT = "\033[7m"

def dump_to_code_bytes(code_dump_ref, code_bytes_ref):
    for l in code_dump_ref.splitlines():
        if len(l) == 0:
            continue
        code_bytes_ref.extend(
                [int(b, 16) for b in l.split(" ")]
                )


def virtual_mmap(virtual_mem_ref, array_ref, N):
    # Check if the replacement list can fit within the main list starting from position N
    if N + len(array_ref) <= len(virtual_mem_ref):
        virtual_mem_ref[N:N + len(array_ref)] = array_ref
    else:
        print("cannot perform mmap, the target position is out of range")


def print_hexdump(data):
    for i in range(0, len(data), 16):
        hex_vals = []
        ascii_vals = []

        for j in range(i, min(i + 16, len(data))):
            val = data[j]
            if val == 0:
                hex_vals.append(f"{DARK_GRAY}00{RESET_COLOR}")
            else:
                hex_vals.append(f"{val:02X}")
            ascii_vals.append(chr(val) if ord(' ') <= val <= ord('~') else ".")

        hex_padding = ""
        if(len(hex_vals) < 16):
            hex_padding = " __" * (16 - len(hex_vals))

        print(f"{i:04X}", end="    ")
        print(" ".join(hex_vals) + hex_padding, end="    ")
        print("".join(ascii_vals))

