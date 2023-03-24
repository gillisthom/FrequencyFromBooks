import os
import re
import csv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from googletrans import Translator
from pathlib import Path

nltk.download('punkt')  # Download the Punkt tokenizer

def select_language():
    languages = {
        'de': 'German',
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian'
    }

    print("Select a language:")
    for code, name in languages.items():
        print(f"{code}: {name}")

    selected_code = None
    while selected_code not in languages:
        selected_code = input("Enter the language code: ")

    return selected_code

language_code = select_language()

# Create necessary directories if they don't exist
Path("Books").mkdir(exist_ok=True)
Path("Output").mkdir(exist_ok=True)
Path("Processed_words").mkdir(exist_ok=True)
Path("FrequencyWords").mkdir(exist_ok=True)

# Load the processed words from a file
processed_words_file = f"Processed_words/{language_code}.txt"
processed_words = set()
if os.path.exists(processed_words_file):
    with open(processed_words_file, "r", encoding='utf-8') as f:
        for line in f:
            processed_words.add(line.strip())

# Load the frequency list from a file
frequency_list_file = f"FrequencyWords/{language_code}.txt"
with open(frequency_list_file, "r", encoding='utf-8') as f:
    frequency_list = f.readlines()

word_occurrences = {}
for line in frequency_list:
    word, occurrences = line.strip().split()
    word_occurrences[word] = int(occurrences)

# Initialize a dictionary to store the count of each word in the output
word_count = {word: 0 for word in word_occurrences}

# Initialize the translator
translator = Translator()

book_files = sorted([file for file in os.listdir("Books") if file.endswith(".txt")])

for book_file in book_files:
    # Load the book from a text file
    with open(f"Books/{book_file}", "r", encoding='utf-8') as f:
        book_text = f.read()

    # Tokenize the book text into sentences
    sentences = sent_tokenize(book_text)

    def translate_text(text, src, dest):
        return translator.translate(text, src=src, dest=dest).text

    def preprocess_text(text):
        return text.replace("\n", " ").replace("\r", " ")

    # Iterate over the sentences and find the ones containing the specified words
    data = []
    chapter = 1  # Example: You can modify this to detect chapters in the book
    for sentence in sentences:
        tokenized_sentence = word_tokenize(sentence)
        for word in word_occurrences:
            if word in tokenized_sentence and word_count[word] < 2:
                preprocessed_sentence = preprocess_text(sentence)
                preprocessed_translation = preprocess_text(translate_text(sentence, language_code, 'en'))
                data.append({
                    "sentence": preprocessed_sentence,
                    "translation": preprocessed_translation,
                    "word": word
                })
                word_count[word] += 1

    output_file = f"Output/{book_file[:-4]}.csv"
    with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = ["sentence", "translation", "word"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)
            
# Save the processed words to a file
with open(processed_words_file, "w", encoding='utf-8') as f:
    for word in processed_words:
        f.write(f"{word}\n")

