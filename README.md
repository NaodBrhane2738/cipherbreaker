# CipherBreaker

A classical cryptanalysis suite featuring automated frequency analysis, key recovery, and a dual Web Studio / CLI interface for classical ciphers.

---

## ⚡ Key Features

- **5 Classical Ciphers**:
  - **Caesar Cipher**: Brute-forces all 26 shift keys ($0 \dots 25$).
  - **Affine Cipher**: Evaluates 624 key combinations ($12 \text{ coprimes} \times 26 \text{ shifts} \times 2 \text{ indexing modes}$) supporting both 0-based ($A=0$) and 1-based ($A=1$) alphabet systems.
  - **ROT13**: Self-inverse fixed Caesar shift of 13.
  - **Atbash**: Alphabet reversal cipher ($A \leftrightarrow Z, B \leftrightarrow Y$) acting as Affine $a=25, b=25$.
  - **Keyword Cipher**: Substitution cipher using a keyword-derived alphabet + dictionary key recovery.
- **Smart Auto-Detect Engine**: Concurrently evaluates input text against all 5 ciphers and ranks decryption candidates by Chi-Square ($\chi^2$) letter frequency scores and dictionary word matches.
- **Dual Web Studio & CLI**: Runs a local web dashboard (`http://127.0.0.1:8000`) while keeping an interactive CLI prompt active in your terminal.
- **Zero Dependencies**: Pure Python standard library implementation with zero external third-party requirements.

---

## 🚀 Quick Start

### Run Interactively (Web Studio + CLI)
Simply run the main script to start the local web server and open the browser interface:
```bash
python cipherbreaker.py
```

### CLI Command Line Usage
```bash
# Run Smart Auto-Detect on a ciphertext from terminal
python cipherbreaker.py -c "DEBQSJFEPQMRE" --auto --no-browser

# Decrypt Caesar ciphertext
python cipherbreaker.py -c "KHOOR ZRUOG" --auto --no-browser
```

---

## 📁 Repository Structure

```
cipherbreaker/
├── cipherbreaker.py            # Main application entrypoint (Server + CLI)
├── main.py                     # Entrypoint alias
├── index.html                  # Web Studio interface
├── styles.css                  # UI stylesheet
├── script.js                   # Client-side cryptanalysis engine
├── README.md                   # Project documentation
└── solvers/                    # Cryptanalysis Solvers
    ├── __init__.py
    ├── scoring.py              # Chi-Square statistic & English dictionary scoring
    ├── caesar.py               # Caesar cipher solver
    ├── affine.py               # Affine cipher solver (0-based & 1-based)
    ├── rot13.py                # ROT13 solver
    ├── atbash.py               # Atbash solver
    ├── keyword.py              # Keyword cipher encoder/decoder & solver
    └── auto_detect.py          # Unified Smart Auto-Detect engine
```

---

## 🔒 Security & Quality Standards

- Web server strictly binds to `127.0.0.1`.
- Anti-caching headers (`Cache-Control: no-cache`) ensure fresh static asset loading.
- HTML entity escaping on all user-supplied inputs prevents cross-site scripting (XSS).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
