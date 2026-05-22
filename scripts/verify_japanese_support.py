from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

readme = (ROOT / "README.md").read_text()
readme_ja = (ROOT / "README.ja.md").read_text()
index = (ROOT / "index.html").read_text()

required = [
    (readme, "README.ja.md"),
    (readme_ja, "一言でいうと"),
    (readme_ja, "日本語対応"),
    (readme_ja, "はじめての使い方"),
    (readme_ja, "30秒レビュー手順"),
    (readme_ja, "画面の見方"),
    (index, "はじめての方へ"),
    (index, "30秒レビュー手順"),
    (readme_ja, "主張の境界"),
    (index, 'data-lang-button="ja"'),
    (index, "造船所ソルバーラボ"),
]

missing = [marker for text, marker in required if marker not in text]
if missing:
    raise SystemExit("missing Japanese support markers: " + ", ".join(missing))

print("shipyard_solver_japanese_support_ok")
