import pickle

from logger import Logger
from open_file import OpenFile
from terminal_opts import TerminalOptions
from write_file import WriteFile


class Dictionary:
    def __init__(self):
        self.masterdict = []
        self.sess_dictionary = []
        self.ex_sentences = []
        self.sess_sentences = []
        self.word_id = 1
        self.sent_id = 1

    @staticmethod
    def strip_string(string):
        return string.replace("\n", "").replace("\t", "").strip()

    def check_for_dup(self, word, ask_user=True):
        if any(
            (k.chinese == word.chinese and (wordmatch := k)) for k in self.masterdict
        ):
            if ask_user:
                Logger().insert(
                    f"In Dictionary: {wordmatch.chinese} - {wordmatch.pinyin} - {wordmatch.definition}",
                    "INFO",
                )
                keepword = TerminalOptions(
                    ["Yes", "No"],
                    f"Keep Potential Duplicate? - {word.chinese} - {word.pinyin} - {word.definition}",
                ).get_selected()
                if keepword == "No":
                    Logger().insert(f"{word.chinese} not saved.", "INFO")
                    return True
            else:
                return True
        else:
            return False

    def add_word(self, word, dups=False):
        if not dups and self.check_for_dup(word):
            return
        word.id = self.word_id
        self.sess_dictionary.append(word)
        self.masterdict.append(word)
        self.word_id += 1

    def add_sentences(self, sentences):
        for sentence in sentences:
            sentence.id = self.sent_id
            self.ex_sentences.append(sentence)
            self.sess_sentences.append(sentence)
            self.sent_id += 1

    def get_master_dict(self):
        return [vars(words) for words in self.masterdict]

    def get_words(self):
        return [vars(words) for words in self.sess_dictionary]

    def get_all_sentences(self, levels=False):
        if levels is False:
            return [vars(sents) for sents in self.ex_sentences]
        return [vars(sents) for sents in self.ex_sentences if sents.level in levels]

    def get_sentences(self):
        return [vars(sents) for sents in self.sess_sentences]

    def save_dictionary(self):
        self.sess_dictionary = []
        Logger().insert("Saving Dictionary...", "INFO")
        WriteFile.write_file(
            "./data/dictionary_words.pickle",
            pickle.dumps(self.masterdict),
            "wb",
            True,
            False,
        )
        WriteFile.write_file(
            "./data/dictionary_id.pickle", pickle.dumps(self.word_id), "wb", True, False
        )

    def load_dictionary(self):
        try:
            Logger().insert("Loading Dictionary...", "INFO")
            dictionary = OpenFile.open_pickle("./data/dictionary_words.pickle")
            dictionary_id = OpenFile.open_pickle("./data/dictionary_id.pickle")
            self.masterdict = dictionary
            self.word_id = dictionary_id
        except ValueError:
            Logger().insert("Error loading Dictionary - No File Exists", "ERROR")
            return self


class Word:
    def __init__(self, chinese, definition, pinyin, audio):
        self.id = 0
        self.chinese = chinese
        self.pinyin = pinyin
        self.definition = definition
        self.audio = audio


class Sentence:
    def __init__(self, word, chinese, english, pinyin, level, audio):
        self.id = 0
        self.word = word
        self.chinese = chinese
        self.english = english
        self.pinyin = pinyin
        self.level = level
        self.audio = audio
