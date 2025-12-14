import { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Loader2, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import './App.css';

const API_BASE = "http://localhost:6543/api";

function App() {
  const [reviewText, setReviewText] = useState("");
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load reviews saat pertama kali buka
  useEffect(() => {
    fetchReviews();
    document.title = 'Product Review Analyzer';
  }, []);

  const fetchReviews = async () => {
    try {
      const res = await axios.get(`${API_BASE}/reviews`);
      setReviews(res.data);
    } catch (err) {
      console.error("Failed to fetch reviews", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reviewText.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Memanggil backend API
      const res = await axios.post(`${API_BASE}/analyze-review`, {
        text: reviewText
      });
      
      // Menambahkan hasil baru ke list paling atas
      setReviews([res.data, ...reviews]);
      setReviewText("");
    } catch (err) {
      setError("Failed to analyze review. Ensure backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Helper untuk menampilkan icon sentiment
  const getSentimentIcon = (label) => {
    if (label === 'POSITIVE') return <ThumbsUp className="text-green-500" />;
    if (label === 'NEGATIVE') return <ThumbsDown className="text-red-500" />;
    return <Minus className="text-gray-500" />;
  };

  return (
    <div className="container">
      <header>
        <h1>Product Review Analyzer</h1>
        <p>Powered by Pyramid, Hugging Face, and Gemini</p>
      </header>

      <main>
        {/* Input Form */}
        <section className="input-section">
          <form onSubmit={handleSubmit}>
            <textarea
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="Paste a product review here (e.g., 'The battery life is amazing, but the screen is too dim...')"
              rows="4"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !reviewText}>
              {loading ? (
                <>Analyzing <Loader2 className="spin" size={16}/></>
              ) : (
                <>Analyze Review <Send size={16}/></>
              )}
            </button>
          </form>
          {error && <p className="error-msg">{error}</p>}
        </section>

        {/* Results Display */}
        <section className="results-section">
          <h2>Analysis History</h2>
          {reviews.length === 0 && <p className="empty-state">No reviews analyzed yet.</p>}
          
          <div className="review-grid">
            {reviews.map((review) => {
              // --- BARIS KONDISI---
              const isUnknown = review.sentiment === 'UNKNOWN' && review.score === '0.0';
              const showHeader = !isUnknown;
              // --- AKHIR BARIS KONDISI ---

              return (
                <div key={review.id} className="review-card">
                  
                  {/* Menampilkan header HANYA jika bukan UNKNOWN/0.0 */}
                  {showHeader && (
                      <div className="card-header">
                        <span className={`badge ${review.sentiment}`}>
                          {getSentimentIcon(review.sentiment)} {review.sentiment}
                        </span>
                        <span className="score">Conf: {review.score}</span>
                      </div>
                  )}

                  <p className="review-text">"{review.text}"</p>
                  
                  <div className="key-points">
                    <strong>Key Points (Gemini):</strong>
                    <div className="points-content">
                      {review.key_points.split('\n').map((point, idx) => (
                        point.trim() && <p key={idx}>{point}</p>
                      ))}
                    </div>
                  </div>
                  <small className="date">{new Date(review.created_at).toLocaleString()}</small>
                </div>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;