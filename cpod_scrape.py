from urllib.parse import unquote

import regex
from dictionary import Dictionary, Sentence, Word
from logger import Logger
from terminal_opts import TerminalOptions


class ScrapeCpod:
    def __init__(self, soup, word=""):
        self.soup = soup
        self.word_example_sentences = []
        self.dialogue = []
        self.expand_sentences = []
        self.grammar_sentences = []
        self.definition = None
        self.word = word

    def __getitem__(self, key):
        if key == "word_example_sentences":
            return self.word_example_sentences
        elif key == "dialogue":
            return self.dialogue
        elif key == "expand_sentences":
            return self.expand_sentences
        elif key == "grammar_sentences":
            return self.grammar_sentences

    def __setitem__(self, key, value):
        if key == "word_example_sentences":
            self.word_example_sentences = value
        elif key == "dialogue":
            self.dialogue = value
        elif key == "expand_sentences":
            self.expand_sentences = value
        elif key == "grammar_sentences":
            self.grammar_sentences = value

    def get_sentences(self):
        return self.word_example_sentences

    def get_grammar(self):
        return self.grammar_sentences

    def get_expansion(self):
        return self.expand_sentences

    def get_defintion(self):
        return self.definition

    def get_dialogues(self):
        return self.dialogue

    def get_definition(self):
        return self.definition

    def scrape_audio(self, element):
        audio_table = element.find(class_="jp-type-single")
        if audio_table is None:
            return ""
        audio_file = unquote(audio_table.find("a", class_="download-link")["href"])
        audio_file = audio_file.replace("/redirect/?url=", "")
        return audio_file

    def scrape_defintion(self):
        search_table = self.soup.find("div", class_="sample-search")
        if search_table is None:
            return None

        audio_file = ""
        pinyin = ""
        definition = ""

        if search_table is not None:
            audio_file = self.scrape_audio(search_table)
            pinyin_def = search_table.find("p").get_text()
            pinyin_def = (
                pinyin_def.replace("Pinyin: ", "")
                .replace("Definition: ", "")
                .split("\n\t\t\t")
            )
            pinyin = pinyin_def[0]
            definition = pinyin_def[1]

        self.definition = Word(self.word, definition, pinyin, audio_file)

    def scrape_sentences(self, level_selection):
        reg_pattern = regex.compile(r"[\p{Han}，。？：！‘\"\\s]+")

        sample_sentences_table = self.soup.find("table", class_="table-grossary")
        if sample_sentences_table is None:
            return []

        all_sample_sentences = sample_sentences_table.find_all("tr")
        for sentence in all_sample_sentences:
            level = sentence.find(class_="badge").string
            sent_cont = sentence.find(class_="click-to-add")
            sentence_all = sent_cont.get_text()
            char_sent = reg_pattern.findall(sentence_all)[0]
            pinyin_sent = sent_cont.find(class_="dict-pinyin-cont").get_text()
            english_sent = sent_cont.find(class_="dict-pinyin-cont").next_sibling
            audio = self.scrape_audio(sentence)
            english_sent = Dictionary.strip_string(english_sent)
            pinyin_sent = Dictionary.strip_string(pinyin_sent)
            example_sentence = Sentence(
                self.word, char_sent, english_sent, pinyin_sent, level, audio
            )
            if (
                audio != ""
                and audio != "null"
                and english_sent != ""
                and english_sent != "null"
                and pinyin_sent != ""
                and pinyin_sent != "null"
                and char_sent != ""
                and char_sent != "null"
            ):
                self.word_example_sentences.append(example_sentence)
        return self.selection("Examples", level_selection)

    def selection(self, type_select, level_selection=False):

        select = {
            "Expansion": "expand_sentences",
            "Dialogue": "dialogue",
            "Examples": "word_example_sentences",
            "Grammar": "grammar_sentences",
        }

        if level_selection is not False:
            level = [
                x for x in self.word_example_sentences if x.level in level_selection
            ]

        if level_selection is False or level_selection is not False and len(level) > 0:
            keepAll = TerminalOptions(
                ["Yes", "No"],
                f"Do You Want to Keep All the {type_select} Sentences?",
                False,
            ).get_selected()
            if keepAll == "Yes":
                Logger().insert("Keeping All", "INFO")
                return

        if level_selection is False:
            for i, x in enumerate(self[select[type_select]]):
                if type_select == "Dialogue":
                    print(f"{i+1}. \n{x.chinese} \n{x.english}\n")
                elif type_select == "Expansion":
                    print(f"{i+1}. {x.word} \n{x.chinese} \n{x.english}\n")
                elif type_select == "Examples":
                    print(f"{i+1}. {x.level}\n{x.chinese} \n{x.english}\n")
                elif type_select == "Grammar":
                    print(f"{i+1}. {x.word}\n\n{x.chinese} \n{x.english}\n")
                sentence_display = [
                    f"{i+1}-{x.chinese}"[0:30]
                    for i, x in enumerate(self[select[type_select]])
                ]

        elif level_selection is not False:
            print(len(level), "len")
            if len(level) == 0:
                add_levels = TerminalOptions(
                    ["Yes", "No"],
                    "There arent sentences for the level(s) selected. Add more levels?:",
                ).get_selected()
                if add_levels == "Yes":
                    level_new_selection = TerminalOptions(
                        [
                            "Newbie",
                            "Elementary",
                            "Pre-Intermediate",
                            "Intermediate",
                            "Advanced",
                        ],
                        "Please Select More Levels:",
                        True,
                    ).get_selected()
                    return self.selection("Examples", level_new_selection)
                else:
                    self[select[type_select]] = []
                    return

            for i, x in enumerate(level):
                print(f"{i+1}. {x.chinese} \n{x.english}\n{x.level}")
            sentence_display = [
                f"{i+1} - {x.chinese}"[0:30] for i, x in enumerate(level)
            ]

        term_selection = TerminalOptions(
            sentence_display,
            "Which the Sentences Do You Want to Keep?",
            True,
        ).indexes

        self[select[type_select]] = [
            self[select[type_select]][i] for i in term_selection
        ]

    def scrape_dialogues(self):
        dialogue_cont = self.soup.find("div", id="dialogue")
        if dialogue_cont is None:
            return None
        dialogue = dialogue_cont.find_all("tr")
        title_cont = self.soup.find("h1", class_="lesson-page-title")
        title = title_cont.find("span", attrs={"itemprop": "name"}).string
        badge = title_cont.find("a", class_="badge").get_text()
        for sentence in dialogue:

            chinese = sentence.find("p", class_="click-to-add").get_text()
            pinyin = sentence.find("p", class_="show-pinyin").get_text()
            english = sentence.find("p", class_="translation-container").get_text()
            title = Dictionary.strip_string(title)
            audio = self.scrape_audio(sentence)
            chinese = Dictionary.strip_string(chinese)
            pinyin = Dictionary.strip_string(pinyin)
            english = Dictionary.strip_string(english)
            dialogue_sent = Sentence(title, chinese, english, pinyin, badge, audio)
            self.dialogue.append(dialogue_sent)
        return self.selection("Dialogue")

    def scrape_expansion(self):
        expansion = self.soup.find(id="expansion")

        if expansion is None:
            return None
        expand_cards = expansion.find_all("div", class_="cpod-card")
        title_cont = self.soup.find("h1", class_="lesson-page-title")
        badge = title_cont.find("a", class_="badge").get_text()
        for card in expand_cards:
            word = card.find("div", class_="font-chinese title-font").get_text()
            table = card.find_all("tr")
            for sent in table:

                chinese = sent.find("p", class_="click-to-add").get_text()
                pinyin = sent.find("p", class_="show-pinyin").get_text()
                english = sent.find("p", class_="translation-container").get_text()
                audio = self.scrape_audio(sent)
                pinyin = Dictionary.strip_string(pinyin)
                chinese = Dictionary.strip_string(chinese)
                english = Dictionary.strip_string(english)
                expand_sentence = Sentence(word, chinese, english, pinyin, badge, audio)
                self.expand_sentences.append(expand_sentence)
        return self.selection("Expansion")

    def scrape_lesson_vocab(self):
        key_vocab = self.soup.find(id="key_vocab")
        if key_vocab is None:
            return None
        vocabs = key_vocab.find_all("tr")
        words = []
        for vocab in vocabs:
            tds = vocab.find_all("td")
            chinese = tds[1].get_text()
            pinyin = tds[2].get_text()
            chinese = Dictionary.strip_string(chinese)
            chinese = chinese.replace(" ", "")
            pinyin = Dictionary.strip_string(pinyin)

            word = Word(chinese, "", pinyin, "")
            words.append(word)
        return words

    def scrape_lesson_grammar(self):
        cont = self.soup.find("div", id="grammar")
        gram_card = cont.find_all("div", id="grammar_introduction")
        title_cont = self.soup.find("h1", class_="lesson-page-title")
        badge = title_cont.find("a", class_="badge").get_text()
        for gram in gram_card:
            # title = gram.find("h3", class_="panel-title").get_text()
            description = gram.find("div", class_="panel-body").find("p").get_text()
            title_n_des = Dictionary.strip_string(description)
            sent_cont = gram.find("div", id="grammar_sentence")
            sents = sent_cont.find_all("tr")
            for sent in sents:

                chinese = sent.find("p", class_="click-to-add").get_text()
                pinyin = sent.find("p", class_="show-pinyin").get_text()
                english = sent.find("p", class_="translation-container").get_text()
                audio = self.scrape_audio(sent)
                pinyin = Dictionary.strip_string(pinyin)
                chinese = Dictionary.strip_string(chinese)
                english = Dictionary.strip_string(english)

                grammar_sent = Sentence(
                    title_n_des, chinese, english, pinyin, badge, audio
                )
                self.grammar_sentences.append(grammar_sent)
        return self.selection("Grammar")
