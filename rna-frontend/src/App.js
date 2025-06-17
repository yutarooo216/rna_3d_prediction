// src/App.js
import React, { useState } from 'react';
import axios from 'axios';

// Get API URL from environment variables
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
      setStatus("Submission completed. The result will be sent by email.");
    } catch (err) {
      console.error(err);
      setError("Submission failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <h1>RNA 3D Structure Prediction</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>RNA Sequence:</label><br />
          <textarea value={sequence} onChange={e => setSequence(e.target.value)} required />
        </div>
        <div>
          <label>Email Address:</label><br />
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <button type="Submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit'}
        </button>
      </form>
      {status && <p style={{ color: 'green' }}>{status}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;