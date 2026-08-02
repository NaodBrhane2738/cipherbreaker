from typing import List, Tuple
from .scoring import calculate_chi_square

def decrypt_caesar(ciphertext: str, shift: int) -> str:
    """
    Decrypts ciphertext using a Caesar shift key (0..25).
    Preserves character casing and non-alphabetic symbols.
    """
    result = []
    shift = shift % 26
    for char in ciphertext:
        if 'a' <= char <= 'z':
            base = ord('a')
            result.append(chr((ord(char) - base - shift) % 26 + base))
        elif 'A' <= char <= 'Z':
            base = ord('A')
            result.append(chr((ord(char) - base - shift) % 26 + base))
        else:
            result.append(char)
    return "".join(result)

def encrypt_caesar(plaintext: str, shift: int) -> str:
    """
    Encrypts plaintext using a Caesar shift key (0..25).
    """
    return decrypt_caesar(plaintext, -shift % 26)

def solve_caesar(ciphertext: str) -> List[Tuple[int, str, float, float]]:
    """
    Brute-forces all 26 possible Caesar shift keys.
    Returns sorted list of tuples: (shift, decrypted_text, score, confidence)
    """
    results = []
    for shift in range(26):
        decrypted = decrypt_caesar(ciphertext, shift)
        score = calculate_chi_square(decrypted)
        results.append((shift, decrypted, score))

    results.sort(key=lambda x: x[2])
    scores = [r[2] for r in results]
    min_s, max_s = scores[0], scores[-1]
    score_range = (max_s - min_s) if (max_s - min_s) > 0 else 1.0

    final_results = []
    for shift, text, score in results:
        confidence = max(0.0, min(100.0, (1.0 - (score - min_s) / score_range) * 100))
        final_results.append((shift, text, score, confidence))

    return final_results
