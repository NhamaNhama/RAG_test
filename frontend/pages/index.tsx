import React from 'react';
import { useState } from 'react';
import { Container, Typography, TextField, Button, Paper, Box } from '@mui/material';

// ▼ 追加: カスタムフックを用意
function useRagSearch() {
  const [response, setResponse] = useState('');

  const doSearch = async (query: string) => {
    try {
      // ▼ ここで環境変数から API URL を取得できるようにする
      const apiUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000/api';
      const res = await fetch(`${apiUrl}/query/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResponse(data.answer);
    } catch (err) {
      console.error(err);
    }
  };

  return { response, doSearch };
}

export default function Home() {
  const [query, setQuery] = useState('');
  // ▼ 上記フックを利用
  const { response, doSearch } = useRagSearch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // AWS API Gateway 経由のURLを想定
    const response = await fetch(process.env.REACT_APP_API_ENDPOINT + '/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query }),
    });
    const data = await response.json();
    setQuery(data.answer);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
        RAG 検索デモ
      </Typography>
      <Paper sx={{ p: 3, mb: 2 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" component="label" htmlFor="rag-query" display="block" gutterBottom>
              検索キーワード:
            </Typography>
            <TextField
              id="rag-query"
              fullWidth
              variant="outlined"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="キーワードを入力してください"
            />
          </Box>
          <Button variant="contained" color="primary" type="submit">
            検索
          </Button>
        </form>
      </Paper>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          応答:
        </Typography>
        <Typography>{response}</Typography>
      </Paper>
    </Container>
  );
} 