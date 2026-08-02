from typing import List, Tuple
from .scoring import calculate_chi_square

VALID_A = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
A_INV = {
    1: 1, 3: 9, 5: 21, 7: 15, 9: 3, 11: 19,
    15: 7, 17: 23, 19: 11, 21: 5, 23: 17, 25: 25
}

def decrypt_affine(ciphertext: str, a: int, b: int, one_indexed: bool = False) -> str:
    """
    Decrypts ciphertext using Affine Cipher parameters a and b.
    Supports both 0-indexed (A=0) and 1-indexed (A=1) alphabet systems.
    """
    if a not in A_INV:
        return ciphertext
    a_inv = A_INV[a]
    result = []
    
    for char in ciphertext:
        if 'a' <= char <= 'z':
            base = ord('a')
            x = ord(char) - base
            if one_indexed:
                x_val = x + 1
                dec_val = (a_inv * (x_val - b)) % 26
                if dec_val == 0:
                    dec_val = 26
                result.append(chr(dec_val - 1 + base))
            else:
                result.append(chr((a_inv * (x - b)) % 26 + base))
        elif 'A' <= char <= 'Z':
            base = ord('A')
            x = ord(char) - base
            if one_indexed:
                x_val = x + 1
                dec_val = (a_inv * (x_val - b)) % 26
                if dec_val == 0:
                    dec_val = 26
                result.append(chr(dec_val - 1 + base))
            else:
                result.append(chr((a_inv * (x - b)) % 26 + base))
        else:
            result.append(char)
    return "".join(result)

def encrypt_affine(plaintext: str, a: int, b: int, one_indexed: bool = False) -> str:
    """
    Encrypts plaintext using Affine Cipher parameters a and b.
    """
    result = []
    for char in plaintext:
        if 'a' <= char <= 'z':
            base = ord('a')
            x = ord(char) - base
            if one_indexed:
                x_val = x + 1
                enc_val = (a * x_val + b) % 26
                if enc_val == 0:
                    enc_val = 26
                result.append(chr(enc_val - 1 + base))
            else:
                result.append(chr((a * x + b) % 26 + base))
        elif 'A' <= char <= 'Z':
            base = ord('A')
            x = ord(char) - base
            if one_indexed:
                x_val = x + 1
                enc_val = (a * x_val + b) % 26
                if enc_val == 0:
                    enc_val = 26
                result.append(chr(enc_val - 1 + base))
            else:
                result.append(chr((a * x + b) % 26 + base))
        else:
            result.append(char)
    return "".join(result)

def solve_affine(ciphertext: str) -> List[Tuple[int, int, bool, str, float, float]]:
    """
    Brute-forces all 624 Affine cipher combinations (12 a values * 26 b shifts * 2 index modes).
    Returns list of tuples: (a, b, one_indexed, decrypted_text, score, confidence)
    """
    results = []
    for a in VALID_A:
        for b in range(26):
            for one_indexed in [False, True]:
                decrypted = decrypt_affine(ciphertext, a, b, one_indexed)
                score = calculate_chi_square(decrypted)
                results.append((a, b, one_indexed, decrypted, score))

    results.sort(key=lambda x: x[4])
    scores = [r[4] for r in results]
    min_s, max_s = scores[0], scores[-1]
    score_range = (max_s - min_s) if (max_s - min_s) > 0 else 1.0

    final_results = []
    for a, b, one_indexed, text, score in results:
        confidence = max(0.0, min(100.0, (1.0 - (score - min_s) / score_range) * 100))
        final_results.append((a, b, one_indexed, text, score, confidence))

    return final_results
