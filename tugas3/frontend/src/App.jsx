import React, { useState, useEffect } from 'react';
import './App.css'; // Asumsi ada basic styling

function App() {
  const [inputText, setInputText] = useState('');
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch reviews saat load
  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const res = await fetch('http://localhost:6543/api/reviews');
      const data = await res.json();
      if (data.status === 'success') {
        setReviews(data.data);
      }
    } catch (err) {
      console.error("Failed fetching reviews", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:6543/api/analyze-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.message || 'Something went wrong');

      // Update list dengan hasil baru
      setReviews([data.data, ...reviews]);
      setInputText('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Product Review Analyzer 🚀</h1>
      
      {/* Input Section */}
      <div className="card input-section">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste product review here..."
          rows="4"
          disabled={loading}
        />
        <button onClick={handleSubmit} disabled={loading || !inputText}>
          {loading ? 'Analyzing...' : 'Analyze Review'}
        </button>
        {error && <p className="error">{error}</p>}
      </div>

      {/* Results Section */}
      <div className="reviews-list">
        <h2>Analysis History</h2>
        {reviews.length === 0 && <p>No reviews yet.</p>}
        
        {reviews.map((review) => (
          <div key={review.id} className="card review-card">
            <div className="review-header">
              <span className={`badge ${review.sentiment}`}>
                {review.sentiment}
              </span>
              <span className="date">
                {new Date(review.created_at).toLocaleString()}
              </span>
            </div>
            <p className="original-text">"{review.text}"</p>
            <div className="key-points">
              <strong>🤖 Gemini Key Points:</strong>
              {/* Render format markdown simple dari Gemini */}
              <pre>{review.key_points}</pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
