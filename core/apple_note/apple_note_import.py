import subprocess

from bs4 import BeautifulSoup
from PySide6.QtCore import QObject, Signal, Slot


class AppleNoteImport(QObject):
    result = Signal(list)
    finished = Signal()
    note_name_verified = Signal(bool)

    def __init__(self, noteName):
        super().__init__()
        self.content = None
        self.noteName = noteName

    @Slot()
    def do_work(self):
        self.open_notes_app()
        self.content = self.get_note_content(self.noteName)

        if self.content:

            self.content = self.clean_html(self.content)
            self.content = self.content.split(",")
            self.clear_note_content(self.noteName)
            self.result.emit(self.content)
        else:
            self.result.emit([])
        self.finished.emit()

    @Slot()
    def verify_note_name(self):
        self.open_notes_app()
        applescript = f"""
        tell application "Notes"
            activate
            set theNote to the first note whose name equals "{self.noteName}"
            set title to the name of theNote
        end tell
        return title
        """
        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )
        test = result.stdout.strip()
        print(result.stdout.strip())
        self.note_name_verified.emit(test == self.noteName)
        self.finished.emit()

    def open_notes_app(self):
        """Launches the Apple Notes application."""
        subprocess.run(["open", "-a", "Notes"])

    def get_note_content(self, note_title):
        """Finds and extracts the text from a note with the given title."""
        applescript = f"""
        tell application "Notes"
            activate
            set theNote to the first note whose name equals "{note_title}"
            set theText to body of theNote
        end tell
        return theText
        """
        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )
        return result.stdout.strip()

    def clean_html(self, content):
        """Removes HTML tags and returns clean text."""
        soup = BeautifulSoup(content, "html.parser")
        title = soup.find("div")
        if title.getText() == self.noteName:
            title.extract()
        return soup.get_text(strip=True, separator=",")

    def clear_note_content(self, note_title):
        """Clears the content of a specific note."""
        applescript = f"""
        tell application "Notes"
            activate
            set theNote to the first note whose name equals "{note_title}"
            set body of theNote to "<h1>{note_title}</h1>"
        end tell
        """
        subprocess.run(["osascript", "-e", applescript])
