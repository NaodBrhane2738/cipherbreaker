from typing import List, Tuple, Set
from .scoring import calculate_chi_square, COMMON_ENGLISH_WORDS

STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def generate_keyword_alphabet(keyword: str) -> str:
    """
    Generates a substitution alphabet using a keyword.
    Unique letters of the keyword appear first, followed by unused alphabet letters.
    Example: keyword="KEYWORD" -> "KEYWORDABCFGHIJLMNPQSTUVXZ"
    """
    clean_kw = "".join([c.upper() for c in keyword if c.isalpha()])
    seen: Set[str] = set()
    cipher_alphabet = []

    for char in clean_kw:
        if char not in seen:
            seen.add(char)
            cipher_alphabet.append(char)

    for char in STANDARD_ALPHABET:
        if char not in seen:
            seen.add(char)
            cipher_alphabet.append(char)

    return "".join(cipher_alphabet)

def encrypt_keyword(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Keyword Cipher.
    """
    cipher_alphabet = generate_keyword_alphabet(keyword)
    result = []
    
    for char in plaintext:
        if 'a' <= char <= 'z':
            idx = ord(char) - ord('a')
            result.append(cipher_alphabet[idx].lower())
        elif 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            result.append(cipher_alphabet[idx])
        else:
            result.append(char)

    return "".join(result)

def decrypt_keyword(ciphertext: str, keyword: str) -> str:
    """
    Decrypts ciphertext using a Keyword Cipher.
    """
    cipher_alphabet = generate_keyword_alphabet(keyword)
    pos_map = {char: idx for idx, char in enumerate(cipher_alphabet)}
    result = []

    for char in ciphertext:
        if 'a' <= char <= 'z':
            upper_c = char.upper()
            if upper_c in pos_map:
                idx = pos_map[upper_c]
                result.append(chr(ord('a') + idx))
            else:
                result.append(char)
        elif 'A' <= char <= 'Z':
            if char in pos_map:
                idx = pos_map[char]
                result.append(chr(ord('A') + idx))
            else:
                result.append(char)
        else:
            result.append(char)

    return "".join(result)

def solve_keyword(ciphertext: str, sample_keywords: List[str] = None) -> List[Tuple[str, str, float, float]]:
    """
    Brute-forces Keyword Cipher using candidate keywords.
    Returns sorted list of tuples: (keyword, decrypted_text, score, confidence)
    """
    if sample_keywords is None:
        sample_keywords = [
            "KEYWORD", "SECRET", "CIPHER", "SECURITY", "CRYPTO", "SYSTEM",
            "PASSWORD", "PROGRAMMING", "PYTHON", "FREEDOM", "KNOWLEDGE",
            "ACADEMY", "DISCOVERY", "LANGUAGE", "VICTORY", "WARRIOR",
            "SHADOW", "LIGHT", "MATRIX", "SPECTRUM", "PHOENIX"
        ]

    results = []
    seen_kw = set()

    for kw in sample_keywords:
        kw_clean = kw.upper().strip()
        if not kw_clean or kw_clean in seen_kw:
            continue
        seen_kw.add(kw_clean)

        decrypted = decrypt_keyword(ciphertext, kw_clean)
        score = calculate_chi_square(decrypted)
        results.append((kw_clean, decrypted, score))

    if not results:
        results.append(("KEYWORD", ciphertext, 9999.0))

    results.sort(key=lambda x: x[2])
    scores = [r[2] for r in results]
    min_s, max_s = scores[0], scores[-1]
    score_range = (max_s - min_s) if (max_s - min_s) > 0 else 1.0

    final_results = []
    for kw, text, score in results:
        confidence = max(0.0, min(100.0, (1.0 - (score - min_s) / score_range) * 100))
        final_results.append((kw, text, score, confidence))

    return final_results
