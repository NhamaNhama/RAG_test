import React, { useState } from 'react';
import styles from '../styles/RichPage.module.css';

export default function RichPage() {
  const [userQuery, setUserQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');
    setAnswer('');

    try {
      // 実際のAPIエンドポイントを環境変数などに合わせて変更
      const apiEndpoint = process.env.NEXT_PUBLIC_API_ENDPOINT || 'http://localhost:8000';
      const response = await fetch(`${apiEndpoint}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userQuery }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setErrorMessage(errorData.error || 'サーバエラーが発生しました');
      } else {
        const data = await response.json();
        setAnswer(data.answer || '回答が取得できませんでした');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('通信エラーが発生しました。サーバにアクセスできません。');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>リッチなデザインページ</h1>
        <p>CSS Modules を使ってスタイルを適用しています。</p>
      </header>

      <main className={styles.main}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            type="text"
            placeholder="聞きたいことを入力"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            className={styles.input}
          />
          <button type="submit" className={styles.btn} disabled={loading || !userQuery}>
            {loading ? '問い合わせ中…' : '送信'}
          </button>
        </form>

        {errorMessage && <p className={styles.error}>エラー: {errorMessage}</p>}
        {answer && (
          <div className={styles.answer}>
            <strong>回答:</strong>
            <p>{answer}</p>
          </div>
        )}
      </main>
    </div>
  );
} 