from audio import Audio
from cpod_scrape import ScrapeCpod
from keys import keys
from logger import Logger
from md_scrape import ScrapeMd
from terminal_opts import TerminalOptions
from write_file import WriteFile


class WordScrape:
    def __init__(self, session, dictionary, file_list):
        self.dictionary = dictionary
        self.level_selection = False
        self.file_list = file_list
        self.session = session
        self.definition_source = 0
        self.save_sentences = "No"
        self.cpod_word = None
        self.start()

    def start(self):
        self.definition_source = TerminalOptions(
            ["Use Cpod Definitions", "Use Mdgb Definitions"],
            "Where should we grab defintions from?",
        ).indexes

        self.save_sentences = TerminalOptions(
            ["Yes", "No"], "Do you want Example Sentences?"
        ).get_selected()
        if self.save_sentences == "Yes":
            filter_by_level = TerminalOptions(
                ["Yes", "No"], "Do you want to filter sentences by level?: "
            ).get_selected()
            if filter_by_level == "Yes":
                self.level_selection = TerminalOptions(
                    [
                        "Newbie",
                        "Elementary",
                        "Pre-Intermediate",
                        "Intermediate",
                        "Advanced",
                    ],
                    "Please Select the Levels:",
                    True,
                ).get_selected()
        self.word_list()
        if len(self.dictionary.get_words()) > 0:
            word_csv_path = WriteFile.write_to_csv(
                "./out/words.csv",
                self.dictionary.get_words(),
            )
            self.dictionary.save_dictionary()
            word_audio = TerminalOptions(
                ["Yes", "No"], "Do You Download the Audio for the Words?"
            ).get_selected()
            if word_audio == "Yes":
                Audio(word_csv_path, "word")
        if self.save_sentences == "Yes" and len(self.dictionary.get_sentences()) > 0:
            sent_csv_path = WriteFile.write_to_csv(
                "./out/ex_sentences.csv", self.dictionary.get_sentences()
            )
            sent_audio = TerminalOptions(
                ["Yes", "No"], "Do You Download the Audio for the Sentences?"
            ).get_selected()
            if sent_audio == "Yes":
                Audio(sent_csv_path, "sentences")

    def cpod_start(self, word):
        c_soup_res = self.session.get_html(
            f"{keys['url']}/dictionary/english-chinese/{word}"
        )
        cpod = ScrapeCpod(c_soup_res, word)
        cpod.scrape_defintion()
        if self.save_sentences == "Yes":
            cpod.scrape_sentences(self.level_selection)
        c_defined_word = cpod.get_defintion()

        if self.save_sentences == "Yes":
            example_sentences = cpod.get_sentences()
            self.dictionary.add_sentences(example_sentences)

        self.cpod_word = c_defined_word

    def md_start(self, word):
        m_soup_res = self.session.get_html(f"{keys['murl']}{word}")
        md = ScrapeMd(m_soup_res)
        m_defined_word = md.get_defintion()

        if self.cpod_word and m_defined_word is not None:
            m_defined_word.audio = self.cpod_word.audio
            self.dictionary.add_word(m_defined_word)
        elif m_defined_word is not None:
            self.dictionary.add_word(m_defined_word)
        elif m_defined_word is None and self.cpod_word is not None:
            print(f"{self.cpod_word.chinese} - {self.cpod_word.definition}")
            use_cpod_instead = TerminalOptions(
                ["Yes", "No"], "Would you like to use Cpod's Definition instead?"
            ).get_selected()
            if use_cpod_instead == "Yes":
                self.dictionary.add_word(self.cpod_word)
            else:
                Logger().insert("Skipping Word", "INFO")
                return
        else:
            Logger().insert("Skipping Word", "INFO")
            return

    def word_list(self):
        for i, word in enumerate(self.file_list):
            Logger().insert(f"({i +1}/{len(self.file_list)}) Word: {word}", "INFO")

            if self.definition_source == 0:
                Logger().insert("Getting Word from Cpod", "INFO")
            elif self.definition_source == 1 and self.save_sentences == "Yes":
                Logger().insert("Getting Sentences and Audio from Cpod", "INFO")
            elif self.definition_source == 1:
                Logger().insert("Getting Audio from Cpod", "INFO")

            self.cpod_start(word)
            if self.definition_source == 0 and self.cpod_word is not None:
                self.dictionary.add_word(self.cpod_word)
            else:
                if self.cpod_word is None:
                    Logger().insert("Word not on Cpod...Trying Mdgb", "INFO")
                else:
                    Logger().insert("Getting Word from Mdgb", "INFO")
                self.md_start(word)
