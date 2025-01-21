import React, { useState } from 'react';

export default function UploadFilePage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    // FileList を配列に展開
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');

    if (selectedFiles.length === 0) {
      setMessage('一つ以上のファイルを選択してください');
      return;
    }

    try {
      const apiEndpoint = process.env.NEXT_PUBLIC_API_ENDPOINT || 'http://localhost:8000';
      const formData = new FormData();
      // 複数ファイルをループで追加
      selectedFiles.forEach((file) => {
        formData.append('files', file);
      });

      const res = await fetch(`${apiEndpoint}/api/upload_file_document/`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        setMessage(data.error || 'アップロードに失敗しました');
      } else {
        setMessage(data.message || 'ファイルのアップロードが完了しました');
      }
    } catch (err) {
      console.error(err);
      setMessage('サーバエラーが発生しました');
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>PDF/Wordファイルのアップロード (複数対応)</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf,.docx" multiple onChange={handleFileChange} />
        <button type="submit">アップロード</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
} 