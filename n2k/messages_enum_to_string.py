import re
from enum import Enum


def camel_case_to_sentence_case(camel: str) -> str:
    """
    Convert a camel case string to a regular sentence where only the first word and acronyms are capitalized.
    Source: https://stackoverflow.com/a/35953318
    
    :param camel: CamelCase string
    :return: Sentence cased string
    """
    result = re.sub("(_)+", " ", camel)
    result = re.sub("([a-z])([A-Z][a-z])", r"\1 \2", result)
    result = re.sub("([A-Z][a-z])([A-Z])", r"\1 \2", result)
    result = re.sub("([a-z])([A-Z]+[a-z])", r"\1 \2", result)
    result = re.sub("([A-Z]+)([A-Z][a-z][a-z])", r"\1 \2", result)
    result = re.sub("([a-z]+)([A-Z0-9]+)", r"\1 \2", result)
    
    # The next regex includes a special case to exclude plurals of acronyms, e.g. "ABCs"
    result = re.sub("([A-Z]+)([A-Z][a-rt-z][a-z]*)", r"\1 \2", result)
    result = re.sub("([0-9])([A-Z][a-z]+)", r"\1 \2", result)
    
    # The next two regexes use {2,} instead of + to add space on phrases like Room26A and 26ABCs but not on phrases
    # like R2D2 and C3PO
    # Disabled due to e.g. 48V, NMEA2000, ...
    # result = re.sub("([A-Z]{2,})([0-9]{2,})", r"\1 \2", result)
    # result = re.sub("([0-9]{2,})([A-Z]{2,})", r"\1 \2", result)
    
    words = result.strip().split(" ")
    # Retain casing for first word
    sentence = "".join(words[:1])
    for word in words[1:]:
        # convert word to lowercase unless it is an acronym
        if len(word) == 1 or \
                (len(word) == 2 and word[0].isupper() and not word.isupper()) or \
                (len(word) >= 3 and word[0].isupper() and not word[:-1].isupper()):
            sentence += " " + word.lower()
        else:
            sentence += " " + word
    return sentence


def enum_to_string(enum: Enum) -> str:
    return camel_case_to_sentence_case(enum.name)
