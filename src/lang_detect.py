# src/lang_detect.py

from collections import Counter


DEVANAGARI_START = ord("\u0900")
DEVANAGARI_END = ord("\u097F")


def char_counts(text: str) -> dict:
    """
    Count script types in text.
    """

    counts = Counter()

    for ch in text:

        if DEVANAGARI_START <= ord(ch) <= DEVANAGARI_END:
            counts["devanagari"] += 1

        elif ch.isascii() and ch.isalpha():
            counts["latin"] += 1

        elif ch.isdigit():
            counts["digits"] += 1

        elif ch.isspace():
            counts["spaces"] += 1

        else:
            counts["other"] += 1

    return counts


HINGLISH_WORDS = {

    # Common Hindi function words

    "hai", "hain", "tha", "thi",
    "the", "ho", "hua", "hui",
    "ko", "ki", "ka", "ke",
    "se", "par", "mein", "men",
    "aur", "aura", "ya", "agar",
    "jab", "jabaki", "tak", "liye",
    "liya", "leti", "leta",
    "gaya", "gayi", "raha", "rahi",
    "kar", "kare", "karna", "kiya",
    "apna", "apne", "unka", "uska",
    "mera", "meri", "ham", "hum",
    "tum", "aap", "sab", "bahut",
    "nahi", "nahin", "mat", "kya",
    "kaise", "kyon",

    # Frequent Roman Hindi corpus words

    "rajya", "desha", "bharata",
    "sarkara", "sarakara", "mantralaya",
    "pradarshana", "janakari",
    "adhikari", "sanpatti", "mahila",
    "purusha", "balaka", "aropi",
    "hirasata", "kapasa",
    "kriketa", "borda", "kendriya",
    "pratyaksha", "kara",
    "vibhaga", "mantri",
    "sadasya", "ghatana",
    "ghayala", "aspatala",
    "parivahana", "rajamarga",
    "utpadana", "bija",
    "istemala"
}


def detect_language(text: str) -> str:
    """
    Returns:

        hi
        hi-Latn
        en
        other
    """

    if not text.strip():
        return "other"

    counts = char_counts(text)

    dev = counts["devanagari"]
    lat = counts["latin"]

    total_letters = dev + lat

    if total_letters == 0:
        return "other"

    dev_ratio = dev / total_letters
    lat_ratio = lat / total_letters

    # Hindi (Devanagari)

    if dev_ratio >= 0.30:
        return "hi"

    # Latin-script text

    if lat_ratio >= 0.80:

        words = [
            word.strip(".,!?;:'\"()[]{}")
            for word in text.lower().split()
        ]

        hinglish_hits = sum(
            1
            for word in words
            if word in HINGLISH_WORDS
        )

        # Strong Roman Hindi signal

        if hinglish_hits >= 2:
            return "hi-Latn"

        # Additional heuristic:
        # many short Hindi grammar words

        grammar_words = {
            "ka", "ki", "ke",
            "ko", "se", "par",
            "hai", "hain", "tha",
            "thi", "men", "mein",
            "aur", "liye"
        }

        grammar_hits = sum(
            1
            for word in words
            if word in grammar_words
        )

        if grammar_hits >= 2:
            return "hi-Latn"

        return "en"

    return "other"