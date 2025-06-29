from models.dictionary import Word


class ScrapeMd:
    def __init__(self, soup):
        self.soup = soup
        self.result_words = []

    def get_results_words(self):
        return self.result_words

    def def_selection(self, index):
        if index is None or index == len(self.result_words):
            return None
        else:
            sel_word = self.result_words[index]
            return Word(
                sel_word["chinese"],
                sel_word["definition"],
                sel_word["pinyin"],
                sel_word["audio"],
                sel_word["level"],
            )

    def scrape_definition(self):
        results_table = self.soup.find("td", class_="resultswrap")

        if results_table is None:
            return None
        results = results_table.find_all("tr", class_="row")

        for result in results:
            hanzi = result.find("div", class_="hanzi").find("a").get_text()
            pinyin = result.find("div", class_="pinyin").find("a").get_text()
            definition = result.find("div", class_="defs").get_text()
            pinyin = pinyin.replace("\u200b", "")
            level = result.find("div", class_="hsk")
            definition_split = definition.split("/")
            definition_string = ""
            for index, meaning in enumerate(definition_split):
                definition_string += f"{index + 1}. {meaning.trim()}"
            definition_string = definition_string.trim()
            word = {
                "chinese": hanzi,
                "definition": definition_string,
                "pinyin": pinyin,
                "audio": "",
                "level": level.get_text() if level is not None else "",
            }
            self.result_words.append(word)
