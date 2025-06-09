// src/App.js
import React, { useState } from 'react';
import axios from 'axios';

// 環境変数からAPI URLを取得
const API_URL = `${process.env.REACT_APP_API_URL}/submit-job/`;

function App() {
  const [sequence, setSequence] = useState('');
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    setError(null);

    try {
      await axios.post(API_URL, { sequence, email });
      setStatus("送信が完了しました。結果はメールでお送りします。");
    } catch (err) {
      console.error(err);
      setError("送信に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <h1>RNA 3D構造予測</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>RNA配列:</label><br />
          <textarea value={sequence} onChange={e => setSequence(e.target.value)} required />
        </div>
        <div>
          <label>メールアドレス:</label><br />
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? '送信中...' : '送信'}
        </button>
      </form>
      {status && <p style={{ color: 'green' }}>{status}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;