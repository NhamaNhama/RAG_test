import React, { useState } from 'react';

export default function UploadPage() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploading(true);
    setMessage('');

    try {
      // NEXT_PUBLIC_API_ENDPOINT を ECS / Amplify / Vercel 等で注入 (本番のAPIエンドポイント)
      const apiEndpoint = process.env.NEXT_PUBLIC_API_ENDPOINT || 'http://localhost:8000';
      const response = await fetch(`${apiEndpoint}/api/upload_document/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setMessage(errorData.error || 'アップロードに失敗しました');
      } else {
        const data = await response.json();
        setMessage(data.message || 'アップロードが成功しました!');
        setTitle('');
        setContent('');
      }
    } catch (error) {
      console.error(error);
      setMessage('サーバに接続できませんでした');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1>ドキュメント追加</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          style={styles.input}
          type="text"
          placeholder="タイトルを入力"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <textarea
          style={styles.textarea}
          placeholder="本文を入力"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={6}
          required
        />
        <button type="submit" style={styles.button} disabled={uploading}>
          {uploading ? 'アップロード中…' : 'アップロード'}
        </button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '600px',
    margin: '40px auto',
    fontFamily: 'sans-serif',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  input: {
    padding: '8px',
    fontSize: '16px',
  },
  textarea: {
    padding: '8px',
    fontSize: '16px',
  },
  button: {
    padding: '10px 16px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#1976d2',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    transition: 'background-color 0.2s',
  },
}; 