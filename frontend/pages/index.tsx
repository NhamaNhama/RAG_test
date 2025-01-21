import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Paper, Box } from '@mui/material';

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');
    setResponse('');

    try {
      // Next.js では NEXT_PUBLIC_API_ENDPOINT を設定
      const apiEndpoint = process.env.NEXT_PUBLIC_API_ENDPOINT || 'http://localhost:8000';
      const res = await fetch(`${apiEndpoint}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        setErrorMessage(errorData.error || 'サーバエラーが発生しました');
      } else {
        const data = await res.json();
        setResponse(data.answer || '回答が取得できませんでした');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('通信エラーが発生しました。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Typography variant="h4" textAlign="center" gutterBottom>
        RAG 検索デモ
      </Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="質問を入力"
          fullWidth
          variant="outlined"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button type="submit" variant="contained" disabled={loading || !query} sx={{ mt: 2 }}>
          {loading ? '問い合わせ中…' : '送信'}
        </Button>
      </form>

      {errorMessage && (
        <Typography color="error" sx={{ mt: 2 }}>
          エラー: {errorMessage}
        </Typography>
      )}
      {response && (
        <Paper sx={{ mt: 3, p: 2 }}>
          <Typography>応答: {response}</Typography>
        </Paper>
      )}
    </Container>
  );
} 