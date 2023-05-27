from dictionary import Word
from terminal_opts import TerminalOptions


class ScrapeMd:
    def __init__(self, soup):
        self.soup = soup
        self.result_words = []

    def def_selection(self):
        if len(self.result_words) > 1:
            words = [
                f"{x['chinese']}({x['pinyin']}) - {x['definition']}"
                for x in self.result_words
            ]
            words.append("None of these")

            term_selection = TerminalOptions(
                words,
                "Select the Definition You Want to Use",
                False,
            ).indexes
            if term_selection == len(self.result_words):
                print("true")
                return None
            else:
                sel_word = self.result_words[term_selection]
                return Word(
                    sel_word["chinese"],
                    sel_word["definition"],
                    sel_word["pinyin"],
                    sel_word["audio"],
                )
        elif len(self.result_words) == 1:
            sel_word = self.result_words[0]
            return Word(
                sel_word["chinese"],
                sel_word["definition"],
                sel_word["pinyin"],
                sel_word["audio"],
            )
        else:
            return None

    def get_defintion(self):
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
        return self.def_selection()
