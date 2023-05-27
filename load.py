from dictionary import Dictionary, Word
from open_file import OpenFile
from write_file import WriteFile

filepath = input("Where is the file located?: ")
while not WriteFile.path_exists(filepath, False):
    filepath = input("File path doesn't exist. Try again: ")
file_list = OpenFile.open_file(filepath, True)

dictionary = Dictionary()
id = 1
for x in file_list:
    if x["chinese"] and x["definition"] and x["pinyin"]:
        if x["audio"]:
            word = Word(x["chinese"], x["definition"], x["pinyin"], x["audio"])
        else:
            word = Word(x["chinese"], x["definition"], x["pinyin"], "")
        word.id = int(x["id"])
        id = int(x["id"])
        print(id, word.chinese)
        dictionary.masterdict.append(word)

dictionary.word_id = id + 1
print(f"Words in Dictionary: {len(dictionary.masterdict)}")
print(f"Next Id: {dictionary.word_id}")
dictionary.save_dictionary()
