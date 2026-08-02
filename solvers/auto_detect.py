from typing import List, Dict, Any
from .scoring import calculate_chi_square
from .caesar import solve_caesar
from .affine import solve_affine
from .rot13 import solve_rot13
from .atbash import solve_atbash
from .keyword import solve_keyword

def auto_detect_cipher(ciphertext: str) -> List[Dict[str, Any]]:
    """
    Evaluates ciphertext against the 5 supported ciphers:
    1. Caesar Cipher
    2. Affine Cipher (0-based & 1-based)
    3. ROT13 Cipher
    4. Atbash Cipher
    5. Keyword Cipher

    Returns a sorted list of candidate decryptions with confidence scores.
    """
    if not ciphertext.strip():
        return []

    candidates = []

    # 1. Caesar
    caesar_res = solve_caesar(ciphertext)
    if caesar_res:
        top = caesar_res[0]
        candidates.append({
            "cipher_name": "Caesar Cipher",
            "key_description": f"Shift {top[0]}",
            "decrypted_text": top[1],
            "score": top[2],
            "details": f"Shift = {top[0]}"
        })

    # 2. Affine
    affine_res = solve_affine(ciphertext)
    if affine_res:
        top = affine_res[0]
        idx_str = "1-based" if top[2] else "0-based"
        candidates.append({
            "cipher_name": "Affine Cipher",
            "key_description": f"a={top[0]}, b={top[1]} ({idx_str})",
            "decrypted_text": top[3],
            "score": top[4],
            "details": f"a={top[0]}, b={top[1]}, index={idx_str}"
        })

    # 3. ROT13
    rot13_text, rot13_score = solve_rot13(ciphertext)
    candidates.append({
        "cipher_name": "ROT13 Cipher",
        "key_description": "Shift 13 (Self-Inverse)",
        "decrypted_text": rot13_text,
        "score": rot13_score,
        "details": "Fixed Caesar shift of 13"
    })

    # 4. Atbash
    atbash_text, atbash_score = solve_atbash(ciphertext)
    candidates.append({
        "cipher_name": "Atbash Cipher",
        "key_description": "Mirror (a=25, b=25)",
        "decrypted_text": atbash_text,
        "score": atbash_score,
        "details": "Alphabet reversal A<->Z"
    })

    # 5. Keyword Cipher
    kw_res = solve_keyword(ciphertext)
    if kw_res:
        top = kw_res[0]
        candidates.append({
            "cipher_name": "Keyword Cipher",
            "key_description": f"Keyword: \"{top[0]}\"",
            "decrypted_text": top[1],
            "score": top[2],
            "details": f"Substitution alphabet from keyword '{top[0]}'"
        })

    candidates.sort(key=lambda x: x["score"])

    scores = [c["score"] for c in candidates]
    min_s, max_s = scores[0], scores[-1]
    score_range = (max_s - min_s) if (max_s - min_s) > 0 else 1.0

    for cand in candidates:
        cand["confidence"] = max(0.0, min(100.0, round((1.0 - (cand["score"] - min_s) / score_range) * 100, 1)))

    return candidates
