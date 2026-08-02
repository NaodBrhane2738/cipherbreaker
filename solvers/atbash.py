from typing import Tuple
from .scoring import calculate_chi_square

def decrypt_atbash(ciphertext: str) -> str:
    """
    Decrypts Atbash cipher by reversing alphabetic letters (A<->Z, B<->Y, etc.).
    Equivalent to an Affine cipher with a=25, b=25. Self-inverse.
    """
    result = []
    for char in ciphertext:
        if 'a' <= char <= 'z':
            result.append(chr(ord('z') - (ord(char) - ord('a'))))
        elif 'A' <= char <= 'Z':
            result.append(chr(ord('Z') - (ord(char) - ord('A'))))
        else:
            result.append(char)
    return "".join(result)

def encrypt_atbash(plaintext: str) -> str:
    """
    Encrypts Atbash cipher.
    """
    return decrypt_atbash(plaintext)

def solve_atbash(ciphertext: str) -> Tuple[str, float]:
    """
    Solves Atbash cipher and returns (decrypted_text, score).
    """
    decrypted = decrypt_atbash(ciphertext)
    score = calculate_chi_square(decrypted)
    return decrypted, score
