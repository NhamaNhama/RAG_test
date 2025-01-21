import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Paper, Box } from '@mui/material';

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
      // Next.js での環境変数は "NEXT_PUBLIC_API_ENDPOINT" を使用。
      const apiUrl = process.env.NEXT_PUBLIC_API_ENDPOINT || 'http://localhost:8000';
      const response = await fetch(apiUrl + '/query', {
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
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
        RAG 検索デモ
      </Typography>
      <form onSubmit={handleSubmit} style={styles.form}>
        <TextField
          type="text"
          placeholder="質問を入力してください"
          value={userQuery}
          onChange={(e) => setUserQuery(e.target.value)}
          style={styles.input}
        />
        <Button type="submit" style={styles.button} disabled={loading || !userQuery}>
          {loading ? '問い合わせ中…' : '送信'}
        </Button>
      </form>

      {errorMessage && <p style={styles.error}>エラー: {errorMessage}</p>}
      {answer && (
        <div style={styles.answerContainer}>
          <strong>回答:</strong>
          <p>{answer}</p>
        </div>
      )}
    </Container>
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