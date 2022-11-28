import stanza

from xatkitnlu.core.nlp_configuration import NlpConfiguration
from xatkitnlu.core.pipelines import create_or_get_stemmer, create_or_get_tokenizer, stemmer_lang_map
from xatkitnlu.dsl.dsl import Intent, CustomEntity
from xatkitnlu.utils.utils import replace_value_in_sentence


def preprocess_text(text: str, configuration: NlpConfiguration) -> str:
    preprocessed_sentence: str = text
    if configuration.stemmer:
        preprocessed_sentence = stem_text(preprocessed_sentence, configuration)
    return preprocessed_sentence


def preprocess_custom_entity_entries(entity: CustomEntity, configuration: NlpConfiguration):
    for entry in entity.entries:
        entry.preprocessed_value = preprocess_text(entry.value, configuration)
        entry.preprocessed_synonyms = []
        for synonym in entry.synonyms:
            entry.preprocessed_synonyms.append(preprocess_text(synonym, configuration))


def preprocess_training_sentences(intent: Intent, configuration: NlpConfiguration):
    intent.processed_training_sentences = []
    for i in range(len(intent.training_sentences)):
        preprocessed_sentence: str = intent.training_sentences[i]

        if configuration.use_ner_in_prediction:
            preprocessed_sentence = replace_ner_in_training_sentence(preprocessed_sentence, intent, configuration)

        preprocessed_sentence = preprocess_text(preprocessed_sentence, configuration)

        intent.processed_training_sentences.append(preprocessed_sentence)


def replace_ner_in_training_sentence(sentence: str, intent: Intent, configuration: NlpConfiguration):
    ner_sentence: str = sentence
    for entity_ref in intent.entity_parameters:
        ner_sentence = replace_value_in_sentence(ner_sentence, entity_ref.fragment, entity_ref.entity.name.upper())
    return ner_sentence


def stem_text(text: str, configuration: NlpConfiguration) -> str:
    tokens: list[str] = tokenize_text(text, configuration)
    # print(Stemmer.algorithms()) # Names of the languages supported by the stemmer
    stemmer_language: str = 'en'
    if configuration.country in stemmer_lang_map:
        stemmer_language = stemmer_lang_map[configuration.country]

    stemmer = create_or_get_stemmer(stemmer_language)
    stemmed_sentence: list[str] = []

    # We stem words one by one to be able to skip words all in uppercase (e.g. references to entity types)
    for word in tokens:
        stemmed_word: str = word
        if not word.isupper():
            stemmed_word = stemmer.stemWord(word)
        stemmed_sentence.append(stemmed_word)

    # stemmed_sentence: list[str] = stemmer.stemWords(tokens)
    # print("Stemmed sentence")
    # print(stemmed_sentence)
    joined_string = ' '.join([str(item) for item in stemmed_sentence])
    return joined_string


def tokenize_text(sentence: str, configuration: NlpConfiguration) -> list[str]:
    tokenizer = create_or_get_tokenizer(configuration.country)
    tokenizer_result: stanza.models.common.doc.Document = tokenizer(sentence)
    token_sentence: stanza.models.common.doc.Sentence = tokenizer_result.sentences[0]
    tokens: list[str] = []
    for token in token_sentence.tokens:
        tokens.append(token.text)
    return tokens
