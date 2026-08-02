import sys
import os
import argparse
import threading
import webbrowser
import socket
import json
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer

from solvers import (
    auto_detect_cipher,
    solve_caesar,
    solve_affine,
    solve_rot13,
    solve_atbash,
    solve_keyword,
    decrypt_keyword,
    encrypt_keyword
)

def find_free_port(default_port=8000) -> int:
    for port in range(default_port, default_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return default_port

class CipherBreakerAPIHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler serving static web dashboard assets
    and JSON REST endpoints for CipherBreaker cryptanalysis solvers.
    """
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/auto_detect':
            params = urllib.parse.parse_qs(parsed.query)
            text = params.get('text', [''])[0]
            
            results = auto_detect_cipher(text)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))
            return
        
        super().do_GET()

    def log_message(self, format, *args):
        pass

def start_web_server() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    port = find_free_port(8000)

    server = HTTPServer(('127.0.0.1', port), CipherBreakerAPIHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)
    return url

def print_banner():
    print("""
===================================================================================
                  🔓 CIPHERBREAKER — CRYPTANALYSIS SUITE (WEB & CLI)                
===================================================================================
   Supported Ciphers: Caesar | Affine | ROT13 | Atbash | Keyword Cipher
===================================================================================
    """)

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="CipherBreaker Cryptanalysis Suite")
    parser.add_argument("-c", "--ciphertext", type=str, help="Ciphertext to analyze")
    parser.add_argument("-a", "--auto", action="store_true", help="Run Smart Auto-Detect across all 5 ciphers")
    parser.add_argument("--no-browser", action="store_true", help="Do not open web browser automatically")
    args = parser.parse_args()

    if args.ciphertext and args.auto:
        print_banner()
        print(f"[⚡] Running Smart Auto-Detect on: \"{args.ciphertext}\"\n")
        results = auto_detect_cipher(args.ciphertext)
        print("=" * 95)
        print(f"{'RANK':<5} | {'CIPHER NAME':<24} | {'KEY PARAMETERS':<24} | {'CONF':<8} | {'DECRYPTED TEXT'}")
        print("=" * 95)
        for rank, res in enumerate(results, start=1):
            badge = " BEST" if rank == 1 else f" #{rank}"
            dec_preview = res["decrypted_text"].replace('\n', ' ')
            if len(dec_preview) > 40:
                dec_preview = dec_preview[:37] + "..."
            print(f"{badge:<5} | {res['cipher_name']:<24} | {res['key_description']:<24} | {res['confidence']:5.1f}% | {dec_preview}")
        print("=" * 95)
        top = results[0]
        print(f"\n[✔] Top Prediction: {top['cipher_name']} ({top['key_description']}, {top['confidence']}% confidence)")
        print(f"--> {top['decrypted_text']}\n")
        return

    print_banner()

    if not args.no_browser:
        web_url = start_web_server()
        print(f"[🌐] CipherBreaker Web Dashboard running at: {web_url}")
        print("[💻] Interactive CLI active below. Enter ciphertext to decrypt!")

    sample = "KHOOR ZRUOG! DEBQSJFEPQMRE"
    print(f"\nDefault Sample: '{sample}'")

    while True:
        try:
            print("\n" + "-" * 95)
            user_input = input("Enter ciphertext to run Auto-Detect (or 'exit' to quit): ").strip()
            
            if user_input.lower() in ('exit', 'quit', 'q'):
                print("\nExiting CipherBreaker. Goodbye!")
                break
            
            ciphertext = sample if (not user_input or user_input.lower() == 'sample') else user_input

            print(f"\n[⚡] Running Auto-Detect on: \"{ciphertext}\"")
            results = auto_detect_cipher(ciphertext)

            print("\n" + "=" * 95)
            print(f"{'RANK':<5} | {'CIPHER NAME':<24} | {'KEY PARAMETERS':<24} | {'CONF':<8} | {'DECRYPTED TEXT'}")
            print("=" * 95)
            for rank, res in enumerate(results, start=1):
                badge = " BEST" if rank == 1 else f" #{rank}"
                dec_preview = res["decrypted_text"].replace('\n', ' ')
                if len(dec_preview) > 40:
                    dec_preview = dec_preview[:37] + "..."
                print(f"{badge:<5} | {res['cipher_name']:<24} | {res['key_description']:<24} | {res['confidence']:5.1f}% | {dec_preview}")
            print("=" * 95)

            top = results[0]
            print(f"\n[✔] Top Prediction: {top['cipher_name']} ({top['key_description']}, {top['confidence']}% confidence)")
            print(f"--> {top['decrypted_text']}")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
