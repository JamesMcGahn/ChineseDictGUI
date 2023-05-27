from logger import Logger
from simple_term_menu import TerminalMenu


class TerminalOptions:
    def __init__(self, options, title, multi=False):
        self.options = options
        self.isMulti = multi
        self.title = title
        self.start = TerminalMenu(
            self.options,
            title=self.title,
            multi_select=self.isMulti,
            show_multi_select_hint=self.isMulti,
        )
        self.indexes = self.show()
        self.chosen = self.start.chosen_menu_entries

    def show(self):
        try:
            Logger().insert(self.title, "INFO", False)
            return self.start.show()
        except AttributeError:
            raise KeyboardInterrupt

    def get_selected(self, arry=False):
        if not self.isMulti and arry:
            if self.options[self.indexes] is None:
                raise KeyboardInterrupt
            Logger().insert(
                f"You selected: {[self.options[self.indexes]]}", "INFO", True
            )
            return [self.options[self.indexes]]
        elif not self.isMulti:
            if self.options[self.indexes] is None:
                raise KeyboardInterrupt
            Logger().insert(f"You selected: {self.options[self.indexes]}", "INFO", True)
            return self.options[self.indexes]
        elif self.isMulti and arry:
            if self.chosen is None:
                raise KeyboardInterrupt
            Logger().insert(f"You selected: {list(self.chosen)}", "INFO", True)
            return list(self.chosen)
        else:
            if self.chosen is None:
                raise KeyboardInterrupt
            return self.chosen
