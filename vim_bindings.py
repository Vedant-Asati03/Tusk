from textual.widgets import TextArea
from textual.app import Binding


class CustomKeyBindings(TextArea):
    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select all"),
        Binding("i", "insert_before_cursor", "Insert before cursor"),
        Binding("I", "insert_at_line_start", "Insert at line start"),
        Binding("a", "insert_after_cursor", "Insert after cursor"),
        Binding("A", "insert_at_line_end", "Insert at line end"),
        Binding("o", "open_line_below", "Open line below"),
        Binding("O", "open_line_above", "Open line above"),
        Binding("ea", "insert_at_word_end", "Insert at word end"),
        Binding("ctrl+h", "delete_before_cursor", "Delete before cursor"),
        Binding("ctrl+w", "delete_word_before_cursor", "Delete word before cursor"),
        Binding("ctrl+j", "add_line_break", "Add line break"),
        Binding("ctrl+t", "indent_line", "Indent line"),
        Binding("ctrl+d", "deindent_line", "De-indent line"),
        Binding("ctrl+n", "autocomplete_next", "Autocomplete next"),
        Binding("ctrl+p", "autocomplete_previous", "Autocomplete previous"),
        Binding("ctrl+rx", "insert_register", "Insert register"),
        Binding("ctrl+ox", "normal_mode_command", "Normal mode command"),
        Binding("esc", "exit_insert_mode", "Exit insert mode"),
        Binding("ctrl+c", "exit_insert_mode", "Exit insert mode"),
    ]

    def action_insert_before_cursor(self) -> None:
        self.move_cursor_relative(columns=-1)
        self.enter_insert_mode()

    def action_insert_at_line_start(self) -> None:
        self.move_cursor_to_line_start()
        self.enter_insert_mode()

    def action_insert_after_cursor(self) -> None:
        self.move_cursor_relative(columns=1)
        self.enter_insert_mode()

    def action_insert_at_line_end(self) -> None:
        self.move_cursor_to_line_end()
        self.enter_insert_mode()

    def action_open_line_below(self) -> None:
        self.insert("\n")
        self.enter_insert_mode()

    def action_open_line_above(self) -> None:
        self.move_cursor_relative(lines=-1)
        self.insert("\n")
        self.move_cursor_relative(lines=-1)
        self.enter_insert_mode()

    def action_insert_at_word_end(self) -> None:
        self.move_cursor_to_word_end()
        self.enter_insert_mode()

    def action_delete_before_cursor(self) -> None:
        self.delete_before_cursor()

    def action_delete_word_before_cursor(self) -> None:
        self.delete_word_before_cursor()

    def action_add_line_break(self) -> None:
        self.insert("\n")

    def action_indent_line(self) -> None:
        self.indent_line()

    def action_deindent_line(self) -> None:
        self.deindent_line()

    def action_autocomplete_next(self) -> None:
        self.autocomplete_next()

    def action_autocomplete_previous(self) -> None:
        self.autocomplete_previous()

    def action_insert_register(self, register: str) -> None:
        self.insert(self.get_register_content(register))

    def action_normal_mode_command(self, command: str) -> None:
        self.enter_normal_mode()
        self.execute_normal_mode_command(command)
        self.enter_insert_mode()

    def action_exit_insert_mode(self) -> None:
        self.exit_insert_mode()
