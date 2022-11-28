import stanza
import Stemmer

stemmer_lang_map = {
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'it': 'italian',
    'de': 'german',
    'nl': 'dutch',
    'pt': 'portuguese',
    'ca': 'catala'
}

tokenizers: dict[str, stanza.pipeline.core.Pipeline] = {}
stemmers: dict[str, Stemmer.Stemmer] = {}


def create_or_get_tokenizer(lang: str = 'en') -> stanza.pipeline.core.Pipeline:
    if lang in tokenizers:
        return tokenizers[lang]
    tokenizer: stanza.pipeline.core.Pipeline = stanza.Pipeline(lang=lang, processors='tokenize',
                                                               tokenize_no_ssplit=True, logging_level='ERROR')
    tokenizers[lang] = tokenizer
    print('TOKENIZER ADDED: ' + lang)
    return tokenizer


def create_or_get_stemmer(lang: str = 'english') -> Stemmer.Stemmer:
    if lang in stemmers:
        return stemmers[lang]
    stemmer = Stemmer.Stemmer(lang)
    stemmers[lang] = stemmer
    print('STEMMER ADDED:   ' + lang)
    return stemmer


