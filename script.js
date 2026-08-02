// Client Cryptanalysis Script

const AUTO_PRESETS = {
    1: "KHOOR ZRUOG! WKLV LV D VHFUHW PHVVDJH.", // Caesar (Shift 3)
    2: "DEBQSJFEPQMRE", // Affine: a=7, b=9 (1-based) -> CRYPTOGRAPHER
    3: "SVOOL DLIOW! UIRVMWH", // Atbash -> HELLO WORLD! FRIENDS
    4: "EBIIL TLOIA! WKLV LV D VHFUHW" // Keyword (KEYWORD)
};

const STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

// Navigation
function switchNav(panelId) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));

    const btns = Array.from(document.querySelectorAll('.nav-btn'));
    const btn = btns.find(b => {
        const onclick = b.getAttribute('onclick');
        return onclick && onclick.includes(`'${panelId}'`);
    });
    if (btn) btn.classList.add('active');

    const view = document.getElementById(`view-${panelId}`);
    if (view) view.classList.add('active');
}

// 1. Smart Auto-Detect Engine
async function runAutoDetect() {
    const input = document.getElementById('auto-input').value;
    const topBox = document.getElementById('auto-top-box');
    const tbody = document.getElementById('auto-results-body');

    if (!input.trim()) {
        topBox.classList.add('hidden');
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b;">Enter ciphertext above to perform auto-detection.</td></tr>';
        return;
    }

    try {
        const response = await fetch(`/api/auto_detect?text=${encodeURIComponent(input)}`);
        if (response.ok) {
            const results = await response.json();
            renderAutoResults(results);
            return;
        }
    } catch (e) {
        // Fallback to client side
    }

    const fallbackResults = clientAutoDetect(input);
    renderAutoResults(fallbackResults);
}

function renderAutoResults(results) {
    const topBox = document.getElementById('auto-top-box');
    const tbody = document.getElementById('auto-results-body');

    if (!results || results.length === 0) return;

    const top = results[0];
    document.getElementById('auto-top-cipher').textContent = top.cipher_name;
    document.getElementById('auto-top-key').textContent = top.key_description;
    document.getElementById('auto-top-conf').textContent = `${top.confidence}%`;
    document.getElementById('auto-top-text').textContent = top.decrypted_text;
    topBox.classList.remove('hidden');

    tbody.innerHTML = results.map((r, rank) => `
        <tr class="${rank === 0 ? 'best-row' : ''}">
            <td style="text-align:center;"><strong>${rank === 0 ? '1 ★' : (rank + 1)}</strong></td>
            <td><strong>${escapeHtml(r.cipher_name)}</strong></td>
            <td>${escapeHtml(r.key_description)}</td>
            <td>${r.confidence}%</td>
            <td class="mono-cell">${escapeHtml(r.decrypted_text)}</td>
            <td><button class="copy-btn" onclick="copyText('${escapeJsString(r.decrypted_text)}', this)">Copy</button></td>
        </tr>
    `).join('');
}

// Client Fallback Auto Detect
function clientAutoDetect(text) {
    const res = [];

    // Caesar
    const cRes = solveCaesarClient(text);
    if (cRes.length > 0) {
        res.push({
            cipher_name: "Caesar Cipher",
            key_description: `Shift ${cRes[0].shift}`,
            decrypted_text: cRes[0].decrypted,
            score: cRes[0].score
        });
    }

    // Affine
    const aRes = solveAffineClient(text);
    if (aRes.length > 0) {
        const topA = aRes[0];
        res.push({
            cipher_name: "Affine Cipher",
            key_description: `a=${topA.a}, b=${topA.b} (${topA.oneIndexed ? '1-based' : '0-based'})`,
            decrypted_text: topA.decrypted,
            score: topA.score
        });
    }

    // ROT13
    const rot13Text = decryptCaesarClient(text, 13);
    res.push({
        cipher_name: "ROT13 Cipher",
        key_description: "Shift 13 (Self-Inverse)",
        decrypted_text: rot13Text,
        score: calculateChiSquare(rot13Text)
    });

    // Atbash
    const atText = decryptAtbashClient(text);
    res.push({
        cipher_name: "Atbash Cipher",
        key_description: "Mirror (a=25, b=25)",
        decrypted_text: atText,
        score: calculateChiSquare(atText)
    });

    // Keyword
    const kwRes = solveKeywordClient(text);
    if (kwRes.length > 0) {
        res.push({
            cipher_name: "Keyword Cipher",
            key_description: `Keyword: "${kwRes[0].keyword}"`,
            decrypted_text: kwRes[0].decrypted,
            score: kwRes[0].score
        });
    }

    res.sort((a, b) => a.score - b.score);
    const minS = Math.min(...res.map(r => r.score));
    const maxS = Math.max(...res.map(r => r.score));
    const range = (maxS - minS) || 1;

    res.forEach(r => {
        r.confidence = Math.max(0, Math.min(100, Math.round((1 - (r.score - minS) / range) * 100)));
    });

    return res;
}

// 2. Caesar
function runCaesar() {
    const text = document.getElementById('caesar-input').value;
    const shift = parseInt(document.getElementById('caesar-shift').value, 10);
    const tbody = document.getElementById('caesar-results-body');

    if (!text.trim()) { tbody.innerHTML = ''; return; }

    const raw = solveCaesarClient(text);
    tbody.innerHTML = raw.map(r => `
        <tr class="${r.shift === shift ? 'best-row' : ''}">
            <td><strong>Shift ${r.shift}</strong> ${r.shift === shift ? '(Active)' : ''}</td>
            <td>${r.score.toFixed(1)}</td>
            <td class="mono-cell">${escapeHtml(r.decrypted)}</td>
            <td><button class="copy-btn" onclick="copyText('${escapeJsString(r.decrypted)}', this)">Copy</button></td>
        </tr>
    `).join('');
}

// 3. Affine
function runAffine() {
    const text = document.getElementById('affine-input').value;
    const a = parseInt(document.getElementById('affine-a').value, 10);
    const b = parseInt(document.getElementById('affine-b').value, 10);
    const oneIndexed = document.getElementById('affine-indexing').value === '1';
    const tbody = document.getElementById('affine-results-body');

    if (!text.trim()) { tbody.innerHTML = ''; return; }

    const raw = solveAffineClient(text);
    tbody.innerHTML = raw.slice(0, 40).map(r => `
        <tr class="${r.a === a && r.b === b && r.oneIndexed === oneIndexed ? 'best-row' : ''}">
            <td><strong>a=${r.a}, b=${r.b}</strong> (${r.oneIndexed ? '1-based' : '0-based'})</td>
            <td>${r.score.toFixed(1)}</td>
            <td class="mono-cell">${escapeHtml(r.decrypted)}</td>
            <td><button class="copy-btn" onclick="copyText('${escapeJsString(r.decrypted)}', this)">Copy</button></td>
        </tr>
    `).join('');
}

// 4. ROT13 & Atbash
function runRotAtbash() {
    const text = document.getElementById('ra-input').value;
    const tbody = document.getElementById('ra-results-body');

    if (!text.trim()) { tbody.innerHTML = ''; return; }

    const rot13 = decryptCaesarClient(text, 13);
    const atbash = decryptAtbashClient(text);

    tbody.innerHTML = `
        <tr class="best-row">
            <td><strong>ROT13</strong> (Shift 13)</td>
            <td class="mono-cell">${escapeHtml(rot13)}</td>
            <td><button class="copy-btn" onclick="copyText('${escapeJsString(rot13)}', this)">Copy</button></td>
        </tr>
        <tr class="best-row">
            <td><strong>Atbash</strong> (Mirror)</td>
            <td class="mono-cell">${escapeHtml(atbash)}</td>
            <td><button class="copy-btn" onclick="copyText('${escapeJsString(atbash)}', this)">Copy</button></td>
        </tr>
    `;
}

// 5. Keyword Cipher
function generateKeywordAlphabetClient(keyword) {
    const cleanKw = keyword.toUpperCase().replace(/[^A-Z]/g, '');
    const seen = new Set();
    const alphabet = [];

    for (let c of cleanKw) {
        if (!seen.has(c)) {
            seen.add(c);
            alphabet.push(c);
        }
    }
    for (let c of STANDARD_ALPHABET) {
        if (!seen.has(c)) {
            seen.add(c);
            alphabet.push(c);
        }
    }
    return alphabet.join('');
}

function decryptKeywordClient(ciphertext, keyword) {
    const cipherAlpha = generateKeywordAlphabetClient(keyword);
    const posMap = {};
    for (let i = 0; i < cipherAlpha.length; i++) {
        posMap[cipherAlpha[i]] = i;
    }

    return ciphertext.replace(/[a-zA-Z]/g, c => {
        const isUpper = c >= 'A' && c <= 'Z';
        const upperC = c.toUpperCase();
        if (posMap[upperC] !== undefined) {
            const idx = posMap[upperC];
            return isUpper ? String.fromCharCode(65 + idx) : String.fromCharCode(97 + idx);
        }
        return c;
    });
}

function encryptKeywordClient(plaintext, keyword) {
    const cipherAlpha = generateKeywordAlphabetClient(keyword);
    return plaintext.replace(/[a-zA-Z]/g, c => {
        const isUpper = c >= 'A' && c <= 'Z';
        const idx = c.toUpperCase().charCodeAt(0) - 65;
        const sub = cipherAlpha[idx];
        return isUpper ? sub : sub.toLowerCase();
    });
}

function solveKeywordClient(text) {
    const sampleKeywords = ["KEYWORD", "SECRET", "CIPHER", "SECURITY", "CRYPTO", "SYSTEM", "PASSWORD", "PROGRAMMING", "PYTHON", "FREEDOM"];
    const results = [];

    for (let kw of sampleKeywords) {
        const dec = decryptKeywordClient(text, kw);
        results.push({ keyword: kw, decrypted: dec, score: calculateChiSquare(dec) });
    }

    return results.sort((a, b) => a.score - b.score);
}

function runKeyword() {
    const text = document.getElementById('kw-input').value;
    const kw = document.getElementById('kw-word').value;
    const tbody = document.getElementById('kw-results-body');
    const seqDisplay = document.getElementById('kw-cipher-seq');

    const cipherSeq = generateKeywordAlphabetClient(kw);
    seqDisplay.textContent = cipherSeq;

    if (!text.trim()) { tbody.innerHTML = ''; return; }

    const dec = decryptKeywordClient(text, kw);
    const score = calculateChiSquare(dec);

    tbody.innerHTML = `
        <tr class="best-row">
            <td><strong>"${escapeHtml(kw.toUpperCase())}"</strong></td>
            <td>${score.toFixed(1)}</td>
            <td class="mono-cell">${escapeHtml(dec)}</td>
            <td><button class="copy-btn" onclick="copyText('${escapeJsString(dec)}', this)">Copy</button></td>
        </tr>
    `;
}

// Sandbox UI Controls
function updateSandboxUI() {
    const cipher = document.getElementById('sb-cipher').value;
    const paramsDiv = document.getElementById('sb-params');

    if (cipher === 'caesar') {
        paramsDiv.innerHTML = '<label>Shift (k): <input type="number" id="sb-caesar-k" value="3" min="0" max="25" oninput="updateSandboxOutput()"></label>';
    } else if (cipher === 'affine') {
        paramsDiv.innerHTML = `
            <label>a: <select id="sb-affine-a" onchange="updateSandboxOutput()">
                <option value="1">1</option><option value="3">3</option><option value="5">5</option>
                <option value="7" selected>7</option><option value="9">9</option><option value="11">11</option>
                <option value="15">15</option><option value="17">17</option><option value="19">19</option>
                <option value="21">21</option><option value="23">23</option><option value="25">25</option>
            </select></label>
            <label>b: <input type="number" id="sb-affine-b" value="9" min="0" max="25" oninput="updateSandboxOutput()"></label>
            <label>Indexing: <select id="sb-affine-idx" onchange="updateSandboxOutput()"><option value="0">0-based</option><option value="1" selected>1-based</option></select></label>
        `;
    } else if (cipher === 'keyword') {
        paramsDiv.innerHTML = '<label>Keyword: <input type="text" id="sb-keyword-w" value="KEYWORD" oninput="updateSandboxOutput()"></label>';
    } else {
        paramsDiv.innerHTML = '';
    }
    updateSandboxOutput();
}

function updateSandboxOutput() {
    const cipher = document.getElementById('sb-cipher').value;
    const mode = document.getElementById('sb-mode').value;
    const input = document.getElementById('sb-input').value;
    const outputEl = document.getElementById('sb-output');

    if (!input) { outputEl.value = ''; return; }

    let result = '';
    if (cipher === 'caesar') {
        const k = parseInt(document.getElementById('sb-caesar-k')?.value || 3, 10);
        result = mode === 'encrypt' ? encryptCaesarClient(input, k) : decryptCaesarClient(input, k);
    } else if (cipher === 'affine') {
        const a = parseInt(document.getElementById('sb-affine-a')?.value || 7, 10);
        const b = parseInt(document.getElementById('sb-affine-b')?.value || 9, 10);
        const oneIndexed = document.getElementById('sb-affine-idx')?.value === '1';
        result = mode === 'encrypt' ? encryptAffineClient(input, a, b, oneIndexed) : decryptAffineClient(input, a, b, oneIndexed);
    } else if (cipher === 'rot13') {
        result = decryptCaesarClient(input, 13);
    } else if (cipher === 'atbash') {
        result = decryptAtbashClient(input);
    } else if (cipher === 'keyword') {
        const kw = document.getElementById('sb-keyword-w')?.value || "KEYWORD";
        result = mode === 'encrypt' ? encryptKeywordClient(input, kw) : decryptKeywordClient(input, kw);
    }

    outputEl.value = result;
}

// Client Math Utilities
function solveCaesarClient(text) {
    const res = [];
    for (let s = 0; s < 26; s++) {
        const dec = decryptCaesarClient(text, s);
        res.push({ shift: s, decrypted: dec, score: calculateChiSquare(dec) });
    }
    return res.sort((a, b) => a.score - b.score);
}

function solveAffineClient(text) {
    const validA = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25];
    const res = [];
    for (let a of validA) {
        for (let b = 0; b < 26; b++) {
            for (let oneIndexed of [false, true]) {
                const dec = decryptAffineClient(text, a, b, oneIndexed);
                res.push({ a, b, oneIndexed, decrypted: dec, score: calculateChiSquare(dec) });
            }
        }
    }
    return res.sort((a, b) => a.score - b.score);
}

function decryptCaesarClient(ciphertext, shift) {
    shift = shift % 26;
    return ciphertext.replace(/[a-zA-Z]/g, c => {
        const base = c >= 'a' ? 97 : 65;
        return String.fromCharCode(((c.charCodeAt(0) - base - shift + 2600) % 26) + base);
    });
}

function encryptCaesarClient(plaintext, shift) {
    return decryptCaesarClient(plaintext, -shift % 26);
}

function decryptAffineClient(ciphertext, a, b, oneIndexed) {
    const aInvMap = { 1:1, 3:9, 5:21, 7:15, 9:3, 11:19, 15:7, 17:23, 19:11, 21:5, 23:17, 25:25 };
    const aInv = aInvMap[a] || 1;

    return ciphertext.replace(/[a-zA-Z]/g, c => {
        const base = c >= 'a' ? 97 : 65;
        const x = c.charCodeAt(0) - base;
        if (oneIndexed) {
            let xVal = x + 1;
            let decVal = (aInv * (xVal - b)) % 26;
            if (decVal < 0) decVal += 26;
            if (decVal === 0) decVal = 26;
            return String.fromCharCode(decVal - 1 + base);
        } else {
            let decVal = (aInv * (x - b)) % 26;
            if (decVal < 0) decVal += 26;
            return String.fromCharCode(decVal + base);
        }
    });
}

function encryptAffineClient(plaintext, a, b, oneIndexed) {
    return plaintext.replace(/[a-zA-Z]/g, c => {
        const base = c >= 'a' ? 97 : 65;
        const x = c.charCodeAt(0) - base;
        if (oneIndexed) {
            let xVal = x + 1;
            let encVal = (a * xVal + b) % 26;
            if (encVal < 0) encVal += 26;
            if (encVal === 0) encVal = 26;
            return String.fromCharCode(encVal - 1 + base);
        } else {
            let encVal = (a * x + b) % 26;
            if (encVal < 0) encVal += 26;
            return String.fromCharCode(encVal + base);
        }
    });
}

function decryptAtbashClient(text) {
    return text.replace(/[a-zA-Z]/g, c => {
        const base = c >= 'a' ? 97 : 65;
        return String.fromCharCode(base + (25 - (c.charCodeAt(0) - base)));
    });
}

function calculateChiSquare(text) {
    const ENGLISH_FREQ = { 'A':8.167, 'B':1.492, 'C':2.782, 'D':4.253, 'E':12.702, 'F':2.228, 'G':2.015, 'H':6.094, 'I':6.966, 'J':0.153, 'K':0.772, 'L':4.025, 'M':2.406, 'N':6.749, 'O':7.507, 'P':1.929, 'Q':0.095, 'R':5.987, 'S':6.327, 'T':9.056, 'U':2.758, 'V':0.978, 'W':2.360, 'X':0.150, 'Y':1.974, 'Z':0.074 };
    const letters = text.toUpperCase().replace(/[^A-Z]/g, '');
    const N = letters.length;
    if (N === 0) return 9999;
    const counts = {};
    for (let char in ENGLISH_FREQ) counts[char] = 0;
    for (let i = 0; i < N; i++) counts[letters[i]] = (counts[letters[i]] || 0) + 1;
    let chi = 0;
    for (let char in ENGLISH_FREQ) {
        let exp = (ENGLISH_FREQ[char] / 100.0) * N;
        chi += Math.pow((counts[char] || 0) - exp, 2) / (exp + 0.0001);
    }
    return chi;
}

// Helpers
function loadAutoPreset(id) {
    document.getElementById('auto-input').value = AUTO_PRESETS[id];
    runAutoDetect();
}

function copyAutoTop() {
    const text = document.getElementById('auto-top-text').textContent;
    navigator.clipboard.writeText(text);
}

function copyText(text, btn) {
    navigator.clipboard.writeText(text);
    btn.textContent = 'Copied';
    setTimeout(() => btn.textContent = 'Copy', 1500);
}

function escapeHtml(str) { return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
function escapeJsString(str) { return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n'); }

window.addEventListener('DOMContentLoaded', () => {
    loadAutoPreset(1);
    updateSandboxUI();
});
