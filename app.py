from audio import Audio
from dictionary import Dictionary
from keys import keys
from lesson_scrape import LessonScrape
from logger import Logger
from open_file import OpenFile
from session import Session
from terminal_opts import TerminalOptions
from word_scrape import WordScrape
from write_file import WriteFile


class App:
    def __init__(self):
        self.dictionary = Dictionary()
        self.dictionary.load_dictionary()
        self.new_session = Session(
            f"{keys['url']}accounts/signin", keys["email"], keys["password"]
        )
        self.new_session.load_session()
        self.start()

    def quit_app(self, e):
        if e:
            print("An error has occurred..please try again.")
            Logger().insert(e, "ERROR", False)

        try:
            confirm_options = TerminalOptions(
                ["Yes", "No"],
                "Do you want to quit the app?",
            ).get_selected()
            if confirm_options == "No":
                self.start()
            if confirm_options == "Yes":
                self.new_session.save_session()
                quit_options = TerminalOptions(
                    ["Yes", "No"],
                    "Do you want to Save?",
                ).get_selected()
                if quit_options == "Yes":
                    self.dictionary.save_dictionary()

                Logger().insert("\nQuitting App...", "INFO")
        except KeyboardInterrupt:
            Logger().insert("Good Bye...", "INFO")
            quit()
        Logger().insert("Good Bye...", "INFO")
        quit()

    def start(self):
        print("Quit the app at anytime by pressing ctrl-c")

        while True:
            try:
                start_options = TerminalOptions(
                    [
                        "Words",
                        "Lessons",
                        "Download Audio From Saved File",
                        "Dictionary",
                        "Quit",
                    ],
                    "Do You Want to Scrape Words or Lessons?",
                )
                start_options = start_options.get_selected()

                if start_options == "Quit":
                    self.quit_app(False)
                if start_options != "Dictionary":
                    filepath = input("Where is the file located?: ")
                    while not WriteFile.path_exists(filepath, False):
                        filepath = input("File path doesn't exist. Try again: ")

                if start_options == "Words" or start_options == "Lessons":
                    term_selection = TerminalOptions(
                        ["newline", "comma - (,)", "semi-colon - (;)", "colon - (:)"],
                        "How is the data is separated?",
                    ).indexes
                    seperator = ("\n", ",", ";", ":")

                    file_list = OpenFile.open_file(
                        filepath, False, seperator[term_selection]
                    )

                if start_options == "Words":
                    WordScrape(self.new_session, self.dictionary, file_list)

                elif start_options == "Lessons":
                    LessonScrape(self.new_session, self.dictionary, file_list)

                elif start_options == "Dictionary":
                    WriteFile.write_to_csv(
                        "./out/master-words-list.csv",
                        self.dictionary.get_master_dict(),
                    )

                elif start_options == "Download Audio From Saved File":
                    Audio(filepath, "word")

            except KeyboardInterrupt:
                self.quit_app(False)
            except Exception as e:
                print(e)
                self.quit_app(e)


App()
