from typing import Tuple
from .scoring import calculate_chi_square
from .caesar import decrypt_caesar

def decrypt_rot13(ciphertext: str) -> str:
    """
    Decrypts/Encrypts ROT13 (Caesar shift 13). ROT13 is self-inverse.
    """
    return decrypt_caesar(ciphertext, 13)

def encrypt_rot13(plaintext: str) -> str:
    """
    Encrypts ROT13 (Caesar shift 13).
    """
    return decrypt_rot13(plaintext)

def solve_rot13(ciphertext: str) -> Tuple[str, float]:
    """
    Solves ROT13 cipher and returns (decrypted_text, score).
    """
    decrypted = decrypt_rot13(ciphertext)
    score = calculate_chi_square(decrypted)
    return decrypted, score
