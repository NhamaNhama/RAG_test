import React, { useState } from 'react';

export default function Home() {
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
      // 環境変数 (NEXT_PUBLIC_API_ENDPOINT) が無ければローカル用をデフォルトに (例: http://localhost:8000)
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
    <div style={styles.container}>
      <h1 style={styles.header}>RAG システム フロントエンド</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          placeholder="質問を入力してください"
          value={userQuery}
          onChange={(e) => setUserQuery(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button} disabled={loading || !userQuery}>
          {loading ? '問い合わせ中…' : '送信'}
        </button>
      </form>

      {errorMessage && <p style={styles.error}>エラー: {errorMessage}</p>}
      {answer && (
        <div style={styles.answerContainer}>
          <strong>回答:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '0 20px',
    fontFamily: 'sans-serif',
  },
  header: {
    textAlign: 'center',
    marginBottom: '20px',
    fontSize: '24px',
  },
  form: {
    display: 'flex',
    gap: '8px',
    marginBottom: '16px',
  },
  input: {
    flex: 1,
    padding: '8px',
    fontSize: '16px',
  },
  button: {
    padding: '8px 16px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  error: {
    color: 'red',
  },
  answerContainer: {
    marginTop: '16px',
    background: '#f5f5f5',
    padding: '16px',
    borderRadius: '4px',
  },
}; 