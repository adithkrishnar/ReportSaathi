import React, { useState } from 'react';
import { Printer, MessageCircle, Star, Check } from 'lucide-react';
import { submitFeedback } from '../api';

interface ShareViewProps {
  summary: string;
}

export const ShareView: React.FC<ShareViewProps> = ({ summary }) => {
  const [rating, setRating] = useState<number>(5);
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [sendingFeedback, setSendingFeedback] = useState(false);

  const handlePrint = () => {
    window.print();
  };

  const handleWhatsAppShare = () => {
    const text = encodeURIComponent(
      `*ReportSaathi Medical Summary*\n\n${summary}\n\n_Disclaimer: This explains your report. It does not replace your doctor._`
    );
    window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
  };

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSendingFeedback(true);
    try {
      await submitFeedback(rating, feedbackText);
      setFeedbackSent(true);
    } catch {
      setFeedbackSent(true);
    } finally {
      setSendingFeedback(false);
    }
  };

  return (
    <div className="card no-print">
      <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', marginBottom: '16px' }}>
        Save, Share or Give Feedback
      </h3>

      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '24px' }}>
        <button type="button" className="btn btn-secondary" onClick={handlePrint}>
          <Printer size={16} />
          Print / Save as PDF
        </button>
        <button
          type="button"
          className="btn"
          style={{ backgroundColor: '#25D366', color: 'white' }}
          onClick={handleWhatsAppShare}
        >
          <MessageCircle size={16} />
          Share via WhatsApp
        </button>
      </div>

      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
        <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>
          Was this plain-language explanation helpful?
        </h4>

        {feedbackSent ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#16a34a', fontSize: '14px', padding: '8px 0' }}>
            <Check size={18} />
            <span>Thank you for helping us improve ReportSaathi!</span>
          </div>
        ) : (
          <form onSubmit={handleFeedbackSubmit}>
            <div style={{ display: 'flex', gap: '6px', marginBottom: '12px' }}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: star <= rating ? '#f59e0b' : '#cbd5e1',
                  }}
                >
                  <Star size={24} fill={star <= rating ? '#f59e0b' : 'none'} />
                </button>
              ))}
            </div>
            <textarea
              placeholder="Optional: How can we make this explanation clearer?"
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={2}
              style={{
                width: '100%',
                padding: '8px 12px',
                fontSize: '13px',
                border: '1px solid #cbd5e1',
                borderRadius: '6px',
                marginBottom: '10px',
                outline: 'none',
                resize: 'none',
              }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={sendingFeedback}
              style={{ fontSize: '13px', padding: '6px 14px' }}
            >
              {sendingFeedback ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

