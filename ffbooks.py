import os
import glob
import nltk
import csv
from googletrans import Translator
from nltk.tokenize import sent_tokenize, word_tokenize
import inquirer

nltk.download('punkt')

LANGUAGE_MAP = {
    "de": {"file": "FrequencyWords/de.txt", "google_code": "de"},
    "es": {"file": "FrequencyWords/es.txt", "google_code": "es"},
    "fr": {"file": "FrequencyWords/fr.txt", "google_code": "fr"},
    "it": {"file": "FrequencyWords/it.txt", "google_code": "it"},
    "pt": {"file": "FrequencyWords/pt.txt", "google_code": "pt"},
    "ru": {"file": "FrequencyWords/ru.txt", "google_code": "ru"},
}

language_choices = [
    inquirer.List(
        "language",
        message="Choose a language",
        choices=[
            ("German", "de"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
        ],
    )
]

language_code = inquirer.prompt(language_choices)["language"]

frequency_list_file = LANGUAGE_MAP[language_code]["file"]
google_translate_code = LANGUAGE_MAP[language_code]["google_code"]

with open(frequency_list_file, "r", encoding="utf-8") as f:
    frequency_list = f.readlines()

word_occurrences = {}
for line in frequency_list:
    word, occurrences = line.strip().split(maxsplit=1)
    word_occurrences[word] = int(occurrences)

word_count = {word: 0 for word in word_occurrences}

translator = Translator()

# Load processed words for the selected language
processed_words_file = f"Processed_words/{language_code}.txt"
if os.path.exists(processed_words_file):
    with open(processed_words_file, "r", encoding="utf-8") as f:
        processed_words = set(f.read().splitlines())
else:
    processed_words = set()

book_files = glob.glob("Books/*.txt")

for book_file in book_files:
    with open(book_file, "r", encoding="utf-8") as f:
        book_text = f.read()

    sentences = sent_tokenize(book_text)

    data = []
    for sentence in sentences:
        tokenized_sentence = word_tokenize(sentence)
        for word in word_occurrences:
            if (
                word in tokenized_sentence
                and word_count[word] < 2
                and word not in processed_words
            ):
                translation = translator.translate(
                    sentence, src=google_translate_code, dest="en"
                ).text
                data.append(
                    {"Sentence": sentence, "Translation": translation, "Word": word}
                )
                word_count[word] += 1
                processed_words.add(word)

    output_filename = os.path.splitext(os.path.basename(book_file))[0] + ".csv"
    output_filepath = os.path.join("Output", output_filename)

    with open(output_filepath, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Sentence", "Translation", "Word"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Save the updated processed words for the selected language
with open(processed_words_file, "w", encoding="utf-8") as f:
    for word in processed_words:
        f.write(f"{word}\n")
