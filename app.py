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


def start():
    def quit_app(e):
        if e:
            print("An error has occurred..please try again.")
            Logger().insert(e, "ERROR", False)
        Logger().insert("\nQuitting App...", "INFO")
        quit_options = TerminalOptions(
            ["Yes", "No"],
            "Do you want to Save?",
        ).get_selected()
        if quit_options == "Yes":
            dictionary.save_dictionary()
            new_session.save_session()

        Logger().insert("Good Bye...", "INFO")
        quit()

    try:
        new_session = Session(
            f"{keys['url']}accounts/signin", keys["email"], keys["password"]
        )
        new_session.load_session()

        dictionary = Dictionary()
        dictionary.load_dictionary()
        start_options = TerminalOptions(
            [
                "Words",
                "Lessons",
                "Download Audio From Saved File",
                "Dictionary",
                "Quit",
            ],
            "Do You Want to Scrape Words or Lessons?",
        ).get_selected()

        if start_options == "Quit":
            quit_app(False)
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

            file_list = OpenFile.open_file(filepath, False, seperator[term_selection])

        if start_options == "Words":
            WordScrape(new_session, dictionary, file_list)

        elif start_options == "Lessons":
            LessonScrape(new_session, dictionary, file_list)

        elif start_options == "Dictionary":
            WriteFile.write_to_csv(
                "./out/master-words-list.csv",
                dictionary.get_master_dict(),
            )

        elif start_options == "Download Audio From Saved File":
            Audio(filepath, "word")
        dictionary.save_dictionary()
        new_session.save_session()

    except KeyboardInterrupt:
        quit_app(False)
    except Exception as e:
        print(e)
        quit_app(e)


start()
