from dictionary import Word


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
            word = {
                "chinese": hanzi,
                "definition": definition,
                "pinyin": pinyin,
                "audio": "",
            }
            self.result_words.append(word)
