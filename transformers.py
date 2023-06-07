import re
from typing import Iterator

import numpy as np
import openai
import pandas as pd
from numpy import array, average

from config import TEXT_EMBEDDING_CHUNK_SIZE, EMBEDDINGS_MODEL, OPENAI_API_KEY
from database import load_vectors

openai.api_key = OPENAI_API_KEY


def get_col_average_from_list_of_lists(list_of_lists):
    """Return the average of each column in a list of lists."""
    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        list_of_lists_array = array(list_of_lists)
        average_embedding = average(list_of_lists_array, axis=0)
        return average_embedding.tolist()


# Create embeddings for a text using a tokenizer and an OpenAI engine


def create_embeddings_for_text(text, tokenizer):
    """Return a list of tuples (text_chunk, embedding) and an average embedding for a text."""
    token_chunks = list(chunks(text, TEXT_EMBEDDING_CHUNK_SIZE, tokenizer))
    text_chunks = [tokenizer.decode(chunk) for chunk in token_chunks]

    print(f"Calling OpenAi API for embeddings...")
    embeddings_response = get_embeddings(text_chunks, EMBEDDINGS_MODEL)
    print(f"Done. Embedding received...")
    embeddings = [embedding["embedding"] for embedding in embeddings_response]
    text_embeddings = list(zip(text_chunks, embeddings))

    average_embedding = get_col_average_from_list_of_lists(embeddings)

    return (text_embeddings, average_embedding)


def get_embeddings(text_array, engine):
    return openai.Engine(id=engine).embeddings(input=text_array)["data"]


# Split a text into smaller chunks of size n, preferably ending at the end of a sentence
def chunks(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    """Yield successive n-sized chunks from text."""
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j


def get_unique_id_for_file_chunk(filename, chunk_index):
    return str(filename + "-!" + str(chunk_index))


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def remove_punctuation(string):
    puncts = ['\u200d', '?', '....', '..', '...', '', '#', '"', '|', "'",
              '[', ']', '>', '=', '*', '+', '\\',
              '•', '~', '£', '·', '_', '{', '}', '©', '^', '®', '`', '<', '→', '°', '€', '™', '›', '♥', '←', '×', '§',
              '″', '′', 'Â', '█',
              '½', 'à', '…', '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═',
              '¦', '║', '―', '¥', '▓',
              '—', '‹', '─', '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤',
              '▲', 'è', '¸', '¾',
              'Ã', '⋅', '‘', '∞', '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗',
              '▬', '❤', 'ï', 'Ø',
              '¹', '≤', '‡', '√', '!', '🅰', '🅱']

    for punct in puncts:
        string = string.replace(punct, "")

    return string.replace("  ", " ").replace("\n", "; ").replace("\t", " ").replace("\xa0", "")


def replace_contractions(string):
    contraction_colloq_dict = {"btw": "by the way", "ain't": "is not", "aren't": "are not", "can't": "cannot",
                               "'cause": "because", "could've": "could have", "couldn't": "could not",
                               "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not",
                               "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'll": "he will",
                               "he's": "he is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will",
                               "how's": "how is", "I'd": "I would", "I'd've": "I would have", "I'll": "I will",
                               "I'll've": "I will have", "I'm": "I am", "I've": "I have", "i'd": "i would",
                               "i'd've": "i would have", "i'll": "i will", "i'll've": "i will have", "i'm": "i am",
                               "i've": "i have", "isn't": "is not", "it'd": "it would", "it'd've": "it would have",
                               "it'll": "it will", "it'll've": "it will have", "it's": "it is", "let's": "let us",
                               "ma'am": "madam", "mayn't": "may not", "might've": "might have", "mightn't": "might not",
                               "mightn't've": "might not have", "must've": "must have", "mustn't": "must not",
                               "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have",
                               "o'clock": "of the clock", "oughtn't": "ought not", "oughtn't've": "ought not have",
                               "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have",
                               "she'd": "she would", "she'd've": "she would have", "she'll": "she will",
                               "she'll've": "she will have", "she's": "she is", "should've": "should have",
                               "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have",
                               "so's": "so as", "this's": "this is", "that'd": "that would",
                               "that'd've": "that would have", "that's": "that is", "there'd": "there would",
                               "there'd've": "there would have", "there's": "there is", "here's": "here is",
                               "they'd": "they would", "they'd've": "they would have", "they'll": "they will",
                               "they'll've": "they will have", "they're": "they are", "they've": "they have",
                               "to've": "to have", "wasn't": "was not", "we'd": "we would", "we'd've": "we would have",
                               "we'll": "we will", "we'll've": "we will have", "we're": "we are", "we've": "we have",
                               "weren't": "were not", "what'll": "what will", "what'll've": "what will have",
                               "what're": "what are", "what's": "what is", "what've": "what have", "when's": "when is",
                               "when've": "when have", "where'd": "where did", "where's": "where is",
                               "where've": "where have", "who'll": "who will", "who'll've": "who will have",
                               "who's": "who is", "who've": "who have", "why's": "why is", "why've": "why have",
                               "will've": "will have", "won't": "will not", "won't've": "will not have",
                               "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have",
                               "y'all": "you all", "y'all'd": "you all would", "y'all'd've": "you all would have",
                               "y'all're": "you all are", "y'all've": "you all have", "you'd": "you would",
                               "you'd've": "you would have"}

    for contraction, replacement in contraction_colloq_dict.items():
        string = string.replace(contraction, replacement)

    return string


def normalize_text(file_body_string):
    file_body_string = remove_emoji(file_body_string)
    file_body_string = replace_contractions(file_body_string)
    file_body_string = remove_punctuation(file_body_string)

    return file_body_string


def handle_file_string(file, tokenizer, redis_conn, text_embedding_field, index_name):
    filename = file[0]
    print(f"processing file: {filename}")
    file_body_string = file[1]

    # Clean up the file string by replacing newlines and double spaces and semi-colons
    # clean_file_body_string = sanitize_text(file_body_string)
    clean_file_body_string = normalize_text(file_body_string)
    print(f"file cleaned of newlines, double spaces, and semicolons")
    #
    # Add the filename to the text to embed
    text_to_embed = "Filename is: {}; {}".format(
        filename, clean_file_body_string)

    print(f"embedding file {filename} with contents: {clean_file_body_string}")

    # Create embeddings for the text
    try:
        print(f"Starting the embedding process...")
        text_embeddings, average_embedding = create_embeddings_for_text(
            text_to_embed, tokenizer)
        print(f"Finished with embedding process")
        # print("[handle_file_string] Created embedding for {}".format(filename))
    except Exception as e:
        print(f"Failed the embedding process for file: {filename}")
        print("[handle_file_string] Error creating embedding: {}".format(e))

    # Get the vectors array of triples: file_chunk_id, embedding, metadata for each embedding
    # Metadata is a dict with keys: filename, file_chunk_index
    vectors = []
    for i, (text_chunk, embedding) in enumerate(text_embeddings):
        id = get_unique_id_for_file_chunk(filename, i)
        vectors.append(({'id': id
            , "vector": embedding, 'metadata': {"filename": filename
                , "text_chunk": text_chunk
                , "file_chunk_index": i}}))

    try:
        print(f"Loading vectors into Redis")
        load_vectors(redis_conn, vectors, text_embedding_field)
        print(f"Finished loading vectors into Redis")

    except Exception as e:
        print(f'Ran into a problem uploading to Redis: {e}')


# Make a class to generate batches for insertion
class BatchGenerator:

    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size

    # Makes chunks out of an input DataFrame
    def to_batches(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        splits = self.splits_num(df.shape[0])
        if splits <= 1:
            yield df
        else:
            for chunk in np.array_split(df, splits):
                yield chunk

    # Determines how many chunks DataFrame contains
    def splits_num(self, elements: int) -> int:
        return round(elements / self.batch_size)

    __call__ = to_batches
