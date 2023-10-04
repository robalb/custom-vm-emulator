import urwid

# Sample long lists of text for left and right panes
left_pane_content = [f"Left Item {i} --------------------------------------------------------|" for i in range(1, 101)]
right_pane_content = [f"Right Item {i} =====================================|" for i in range(1, 101)]

# Create a ListBox widget from a ListBoxBody widget for the left pane
left_list_box = urwid.ListBox(urwid.SimpleFocusListWalker([
    urwid.Text(item) for item in left_pane_content
]))

# Create a ListBox widget from a ListBoxBody widget for the right pane
right_list_box = urwid.ListBox(urwid.SimpleFocusListWalker([
    urwid.Text(item) for item in right_pane_content
]))

# Create a Columns widget to hold both panes
columns = urwid.Columns([
    ('weight', 1, urwid.LineBox(left_list_box)),
    ('weight', 1, urwid.LineBox(right_list_box)),
])

# Create a Frame widget to add a border around the columns
frame = urwid.Frame(
        columns,
        header=urwid.Text("Two Pane TUI Application"),
        footer=urwid.Edit(
            "yandb:"
            )
        )

# Define a function to handle keyboard input
def handle_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

# Enable mouse scrolling by setting mouse support to True
urwid.raw_display.Screen().set_terminal_properties(256)

# Create the main loop
loop = urwid.MainLoop(frame, unhandled_input=handle_input, pop_ups=True)

# Run the TUI application
loop.run()
