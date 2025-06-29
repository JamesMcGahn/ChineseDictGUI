from urllib.parse import unquote

import regex

import utils
from models.dictionary import Dialogue, Sentence, Word


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
        return {
            "word_example_sentences": self.word_example_sentences,
            "dialogue": self.dialogue,
            "expand_sentences": self.expand_sentences,
            "grammar_sentences": self.grammar_sentences,
        }.get(key, None)

    def __setitem__(self, key, value):
        if key in [
            "word_example_sentences",
            "dialogue",
            "expand_sentences",
            "grammar_sentences",
        ]:
            setattr(self, key, value)

    def get_sentences(self):
        return self.word_example_sentences

    def get_grammar(self):
        return self.grammar_sentences

    def get_expansion(self):
        return self.expand_sentences

    def get_dialogues(self):
        return self.dialogue

    def get_definition(self):
        return self.definition

    def scrape_audio(self, element):
        audio_table = element.find(class_="jplayer-audio-player")
        if audio_table is None:
            return ""
        audio = audio_table.find("audio")
        if audio and audio.has_attr("src"):
            audio_file = audio["src"]
            # print("audio1", audio_file)
            audio_file = audio_file.replace("http://", "https://")
            # print("audio2", audio_file)
            return audio_file
        else:
            audio_file = unquote(audio_table.find("a", class_="download-link")["href"])
            audio_file = audio_file.replace("/redirect/?url=", "")
            audio_file = audio_file.replace("http://", "https://")
            return audio_file

    def scrape_definition(self):
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

    def scrape_sentences(
        self,
    ):
        reg_pattern = regex.compile(r"[\p{Han}，。？：！‘\"\\s]+")

        sample_sentences_table = self.soup.find("table", class_="table-grossary")
        if sample_sentences_table is None:
            return None

        all_sample_sentences = sample_sentences_table.find_all("tr")
        for sentence in all_sample_sentences:
            level = sentence.find(class_="badge").string
            sent_cont = sentence.find(class_="click-to-add")
            sentence_all = sent_cont.get_text()
            char_sent = reg_pattern.findall(sentence_all)[0]
            pinyin_sent = sent_cont.find(class_="dict-pinyin-cont").get_text()
            english_sent = sent_cont.find(class_="dict-pinyin-cont").next_sibling
            audio = self.scrape_audio(sentence)
            english_sent = utils.strip_string(english_sent)
            pinyin_sent = utils.strip_string(pinyin_sent)
            example_sentence = Sentence(
                char_sent,
                english_sent,
                pinyin_sent,
                audio,
                level,
            )
            example_sentence.word = self.word
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
            title = utils.strip_string(title)
            audio = self.scrape_audio(sentence)
            chinese = utils.strip_string(chinese)
            pinyin = utils.strip_string(pinyin)
            english = utils.strip_string(english)

            dialogue_sent = Sentence(chinese, english, pinyin, audio, badge)
            dialogue_sent.word = title
            self.dialogue.append(dialogue_sent)

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
                pinyin = utils.strip_string(pinyin)
                chinese = utils.strip_string(chinese)
                english = utils.strip_string(english)

                expand_sentence = Sentence(chinese, english, pinyin, audio, badge)
                expand_sentence.word = word
                self.expand_sentences.append(expand_sentence)

    def scrape_lesson_vocab(self):
        key_vocab = self.soup.find(id="key_vocab")
        if key_vocab is None:
            return None
        vocabs = key_vocab.find_all("tr")
        print(len(vocabs), "length of tr")
        words = []
        for vocab in vocabs:
            tds = vocab.find_all("td")
            for i, td in enumerate(tds):
                print(f"td[{i}] = {td.get_text(strip=True)}")

            print(tds[1].get_text(), len(tds))
            if len(tds) >= 4:
                chinese = tds[1].get_text()
                pinyin = tds[2].get_text()
                define = tds[3].get_text()
                define = utils.strip_string(define)
                chinese = utils.strip_string(chinese)
                chinese = chinese.replace(" ", "")
                pinyin = utils.strip_string(pinyin)
                audio = self.scrape_audio(vocab)

                word = Word(chinese, define, pinyin, audio)
                words.append(word)
            else:
                print("Skipping row, not enough tds:", len(tds))
                continue

        return words

    def scrape_lesson_grammar(self):
        cont = self.soup.find("div", id="grammar")
        gram_card = cont.find_all("div", id="grammar_introduction")
        title_cont = self.soup.find("h1", class_="lesson-page-title")
        badge = title_cont.find("a", class_="badge").get_text()
        for gram in gram_card:
            # title = gram.find("h3", class_="panel-title").get_text()
            description = gram.find("div", class_="panel-body").find("p").get_text()
            title_n_des = utils.strip_string(description)
            sent_cont = gram.find("div", id="grammar_sentence")
            sents = sent_cont.find_all("tr")
            for sent in sents:
                chinese = sent.find("p", class_="click-to-add").get_text()
                pinyin = sent.find("p", class_="show-pinyin").get_text()
                english = sent.find("p", class_="translation-container").get_text()
                audio = self.scrape_audio(sent)
                pinyin = utils.strip_string(pinyin)
                chinese = utils.strip_string(chinese)
                english = utils.strip_string(english)

                grammar_sent = Sentence(chinese, english, pinyin, audio, badge)
                grammar_sent.word = title_n_des
                self.grammar_sentences.append(grammar_sent)

    def scrape_lesson_and_dialogue_audio(self):
        try:
            title_cont = self.soup.find("h1", class_="lesson-page-title")
            badge = title_cont.find("a", class_="badge").get_text()

            title = title_cont.find("span").get_text()

            container = self.soup.find("div", id="player")
            audio_panel_div = container.find("div", class_="list-group")
            lesson_audio = audio_panel_div.find("a", attrs={"data-type": "lesson"})
            dialogue_audio = audio_panel_div.find("a", attrs={"data-type": "dialogue"})

            def clean_link(link):
                if link and link.has_attr("href"):
                    audio_file = link["href"]
                    print("audio1", audio_file)
                    return audio_file.replace("http://", "https://")
                else:
                    return None

            lesson = Dialogue(
                f"{utils.strip_string(badge)} - {utils.strip_string(title)} - Lesson",
                "lesson",
                clean_link(lesson_audio),
                utils.strip_string(badge),
            )
            dialogue = Dialogue(
                f"{utils.strip_string(badge)} - {utils.strip_string(title)} - Dialogue",
                "dialogue",
                clean_link(dialogue_audio),
                badge,
            )
            print(vars(lesson))
            print(vars(dialogue))
            return (lesson, dialogue)
        except Exception as e:
            print(e)
