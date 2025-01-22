# RAG システム (Django + Next.js + OpenSearch)

このプロジェクトは、リーンな RAG (Retrieval-Augmented Generation) システムのサンプル実装です。  
Django (バックエンド) + Next.js (フロントエンド) + OpenSearch (全文検索 / ベクトル検索) を組み合わせ、  
さらに AWS S3 へファイルをアップロードできるようにしています。

## 構成概要

1. **backend/**  
   - Django プロジェクト (mysite/) とアプリケーション (rag_app/)  
   - RAG 用のモデル (Document, Embedding)  
   - OpenSearch およびクラウドサービス (S3, Anthropic API など) と連携するための設定  
   - views.py には以下の代表的なエンドポイントを実装:  
     - /api/query: ユーザーのクエリを受け取り、LLM+OpenSearch を介した応答を返す  
     - /api/upload_document/: テキストをアップロードし、DB + OpenSearch に登録  
     - /api/upload_file_document/: PDF / Word ファイルをアップロードし、テキスト抽出 + DB + OpenSearch に登録  

2. **frontend/**  
   - Next.js を使ったフロントエンド。pages/ ディレクトリに各種ページを用意:  
     - index.tsx: RAG 検索のメインページ (MUI でフォーム・ボタンなど)  
     - upload.tsx: テキストベースのアップロードUI  
     - uploadFile.tsx: PDF/Word など複数ファイルアップロード用のUI  
     - rich.tsx: CSS Modules を用いたリッチなデザインページ (RichPage.module.css と共に利用)  
   - 環境変数 (NEXT_PUBLIC_API_ENDPOINT など) を使い、バックエンド API のエンドポイントを指定  

3. **OpenSearch**  
   - Docker でローカルに OpenSearch を立ち上げるか、Amazon OpenSearch Service を利用  
   - ベクトル検索 (dense_vector フィールド) や日本語形態素解析 (kuromoji) などに対応  

4. **S3 連携**  
   - Django バックエンドでアップロードされたファイルを S3 に保存し、DB にはキーを保持  
   - PDF/Word ファイルの場合は PyPDF2 / python-docx を使ってテキスト抽出 → Embedding 生成 → OpenSearch 登録  

5. **.github/workflows/ci.yml**  
   - GitHub Actions で各種テストを実行 (pytest 等)  
   - 環境変数や Secrets を指定することで、ビルド / テスト もしくはデプロイ手順を自動化可能  

## セットアップ & 起動手順 (ローカル)

1. **リポジトリをクローン**  
   git clone https://github.com/yourusername/rag-system.git  
   cd rag-system  

2. **Docker Compose を使う場合**  
   - Dockerfile, docker-compose.yml が同梱されている想定  
   - OpenSearch を含めたローカル環境を構築するには:  
     docker-compose up --build  
   - ローカルで Django サーバ (バックエンド) は http://localhost:8000 で起動  
   - フロントエンド (Next.js) は別途起動している場合、http://localhost:3000 など  

3. **フロントエンド手動起動 (Next.js)**  
   - frontend ディレクトリへ移動し依存をインストール:  
     cd frontend  
     npm install  
     npm run dev  

   - ブラウザで http://localhost:3000 にアクセス  

4. **バックエンド手動起動 (Django)**  
   - backend ディレクトリへ移動し依存をインストール:  
     cd backend  
     pip install -r requirements.txt  
     python manage.py migrate  
     python manage.py runserver  

   - ブラウザで http://localhost:8000/api/query などにアクセス  

## 主な環境変数

- **NEXT_PUBLIC_API_ENDPOINT**  
  フロントエンドが参照する API のベース URL  
  (例: https://example.com, ローカル時は http://localhost:8000)

- **S3_BUCKET**  
  Django でファイルアップロードするときの S3 バケット名  

- **ES_ENDPOINT**  
  OpenSearch エンドポイント (例: http://opensearch:9200 または https://search-xxx.ap-northeast-1.es.amazonaws.com)

- **ANTHROPIC_API_KEY**  
  Anthropic (Claude) API キー (LLM 推論に使用)

## ページの使い方

- **http://localhost:3000/**  
  RAG 検索フォーム。ユーザー入力をバックエンドの /api/query へ送信し、回答を表示  

- **http://localhost:3000/upload**  
  シンプルなテキストアップロード UI。タイトルと本文を入力 → /api/upload_document  

- **http://localhost:3000/uploadFile**  
  PDF/Word (複数ファイル) のアップロード。サーバでテキスト抽出 → Embedding → OpenSearch へ登録  

- **http://localhost:3000/rich**  
  リッチなデザインのデモページ (CSS Modules 使用)

## テスト

- Django 側 (バックエンド) のユニットテスト:  
  cd backend  
  pytest  

  または:  
  python manage.py test  

- フロントエンドの Lint / Unit Test (必要に応じ):  
  cd frontend  
  npm run lint  
  npm run test  

## デプロイのヒント

- **AWS ECS (Fargate)**  
  - Docker イメージを ECR にプッシュ → ECS サービスを作成し、ALB で /api/ と / をルーティング  
  - next build / next start をコンテナ内で実行し、CDN や CloudFront で配信してもOK  

- **Amazon OpenSearch Service**  
  - ES_ENDPOINT をサービスのドメインに設定  
  - VPC 内でプライベート接続 or IP-based auth / IAM SigV4 認証などを設定  

- **S3**  
  - IAM ポリシーで putObject / getObject 権限 (バケット名指定)  
  - PDF/Word をアップロード / 解析 → content を Embedding に反映  

## ライセンス・著作権等

- 本サンプルは自由にカスタマイズ可能です。実運用時は認証 / 認可、監査ログ、セキュリティ要件などを検討してください。  
- PyPDF2 や python-docx などの外部ライブラリについては、それぞれのライセンスに従ってご利用ください。

---
以上で README の概要です。問題報告や改善提案は Pull Request / Issue にてお知らせください。

# Usage
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(repo_id="my_org/my_repo", filename="my_model.bin")