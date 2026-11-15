# GGUF テンプレート修正版のビルド＆公開パイプライン

dahara1/Qwen3.5-4B-UD-japanese-imatrix の GGUF（Qwen3.5-4B-UD-Q4_K_XL.gguf）について、
GGUF 埋め込みチャットテンプレートを作者配布の修正済み jinja に差し替えた版を作り、
自分の Hugging Face アカウントに **非公開** でアップロードするための GitHub Actions ワークフローです。
重い処理（約2.9GB のダウンロード・書き換え・アップロード）は全て GitHub のランナー上で行われます。

## ファイル構成

- `.github/workflows/build-fixed-gguf.yml` — ワークフロー本体
- `model-card.md` — Hugging Face 側リポジトリの README（モデルカード）になる文章。実行時に `{{HF_REPO_ID}}` が自分のリポジトリ名に置換されます
- `scripts/verify_template.py` — 書き換え後の埋め込みテンプレートに修正行が入ったかを検査するスクリプト（ワークフロー内で自動実行）

## 手順（1回だけ）

1. Hugging Face で書き込みトークンを発行する
   - huggingface.co → Settings → Access Tokens → Create new token → **Write** を選択して発行
   - トークンの文字列は誰にも送らない（この後の手順で GitHub の Secrets に直接貼るだけ）
2. このリポジトリの Settings → Secrets and variables → Actions → New repository secret で、
   名前 `HF_TOKEN`、値に上のトークンを登録する
3. Actions タブ → 「Build template-fixed GGUF and upload to Hugging Face」→ Run workflow
   - 入力 `hf_repo_id` に自分の HF リポジトリ名を入れる（例：`yourname/Qwen3.5-4B-UD-Q4_K_XL-template-fixed`）
   - リポジトリが無ければ自動で **非公開** として作成されます
4. 成功したら Hugging Face の該当リポジトリに GGUF とモデルカードが入っています
5. PocketPal から自分のリポジトリを指定してダウンロードする（非公開の間は PocketPal 側に HF トークンの設定が必要）
6. 動作に問題がなければ、HF のリポジトリ設定（Settings → Change visibility）で公開に切り替えられます

## ワークフローの安全装置

- 元ファイルの sha256 が既知の値（e57e3a55…）と一致しない場合は停止します
- 差し替えに使う jinja に修正行が含まれていない場合は停止します
- 書き換え後の埋め込みテンプレートを再抽出して修正行を確認し、ファイルサイズが
  元と 1MB 以上変わっていた場合も停止します（重みが書き換わっていないことの傍証）

## 備考

- 元モデル： dahara1/Qwen3.5-4B-UD-japanese-imatrix（Apache-2.0）
- 変更点は埋め込みチャットテンプレートの1行のみ。モデルの重み・量子化は無変更です
