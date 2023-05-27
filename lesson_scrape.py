import os

from audio import Audio
from bs4 import BeautifulSoup
from cpod_scrape import ScrapeCpod
from terminal_opts import TerminalOptions
from web_scrape import WebScrape
from word_scrape import WordScrape
from write_file import WriteFile


class LessonScrape:
    def __init__(self, session, dictionary, file_list):
        self.session = session
        self.file_list = file_list
        self.dictionary = dictionary
        self.start()

    def start(self):
        wb = WebScrape(self.session)
        wb.init_driver()
        word_expansion = []

        for c_lesson in self.file_list:
            wb.run_webdriver(c_lesson)
            lesson = wb.get_source()
            tempfile_path = WriteFile.write_file(
                "./data/temp/temp.html", lesson["source"]
            )
            data = open(tempfile_path, "r")
            soup = BeautifulSoup(data, "html.parser")
            wcpod = ScrapeCpod(soup)
            wcpod.scrape_dialogues()
            dialogues = wcpod.get_dialogues()
            if len(dialogues) > 0:
                self.dictionary.add_sentences(dialogues)

            if "Vocabulary" not in lesson["not_available"]:
                words = wcpod.scrape_lesson_vocab()
                non_dup_words = [
                    word.chinese
                    for word in words
                    if not self.dictionary.check_for_dup(word, False)
                ]
                word_expansion.extend(non_dup_words)
            if "Expansion" not in lesson["not_available"]:
                wcpod.scrape_expansion()
                expand = wcpod.get_expansion()
                self.dictionary.add_sentences(expand)

            if "Grammar" not in lesson["not_available"]:
                wcpod.scrape_lesson_grammar()
                grammar = wcpod.get_grammar()
                self.dictionary.add_sentences(grammar)

            try:
                os.remove(tempfile_path)
            except OSError as error:
                raise RuntimeError(error)
        wb.close()
        sent_csv_path = WriteFile.write_to_csv(
            "./out/lessons.csv", self.dictionary.get_all_sentences()
        )
        sent_audio = TerminalOptions(
            ["Yes", "No"], "Do You Download the Audio for the Sentences?"
        ).get_selected()
        if sent_audio == "Yes":
            Audio(sent_csv_path, "sentences")
        if len(word_expansion) > 0:
            save_exp_vocab = TerminalOptions(
                ["Yes", "No"], "Do you want add the Lesson Vocabs?"
            ).get_selected()
            if save_exp_vocab == "Yes":
                keepAll = TerminalOptions(
                    ["Yes", "No"], "Keep All of the Words?"
                ).get_selected()
                if keepAll == "No":
                    word_list = TerminalOptions(
                        [word for word in word_expansion],
                        "Select the Words You Want to Keep:",
                        True,
                    ).get_selected()
                    WordScrape(self.session, self.dictionary, word_list)
                else:
                    WordScrape(self.session, self.dictionary, word_expansion)
