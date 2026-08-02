from typing import Dict, Set

ENGLISH_FREQ = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702,
    'F': 2.228, 'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153,
    'K': 0.772, 'L': 4.025, 'M': 2.406, 'N': 6.749, 'O': 7.507,
    'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056,
    'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150, 'Y': 1.974,
    'Z': 0.074
}

COMMON_ENGLISH_WORDS: Set[str] = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there",
    "their", "what", "so", "up", "out", "if", "about", "who", "get",
    "which", "go", "me", "when", "make", "can", "like", "time", "no",
    "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first",
    "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "us", "hello", "world", "cipher", "encryption",
    "decryption", "secret", "message", "programming", "code", "python",
    "cryptographer", "cryptography", "keyword", "atbash"
}

def calculate_chi_square(text: str) -> float:
    """
    Calculates Chi-Squared statistic against standard English letter frequencies.
    Lower score indicates a closer statistical fit to standard English.
    """
    letters = [ch.upper() for ch in text if ch.isalpha()]
    total = len(letters)
    if total == 0:
        return 9999.0

    counts: Dict[str, int] = {letter: 0 for letter in ENGLISH_FREQ}
    for letter in letters:
        if letter in counts:
            counts[letter] += 1

    chi_square = 0.0
    for letter, expected_pct in ENGLISH_FREQ.items():
        expected_count = (expected_pct / 100.0) * total
        actual_count = counts[letter]
        chi_square += ((actual_count - expected_count) ** 2) / (expected_count + 1e-6)

    words = [w.strip(".,!?;:\"'()[]{}").lower() for w in text.split()]
    matched_words = sum(1 for word in words if word in COMMON_ENGLISH_WORDS)
    word_bonus = matched_words * 15.0

    return max(0.0, chi_square - word_bonus)
