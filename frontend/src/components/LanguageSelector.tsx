import React from 'react';
import { Languages, BookOpen } from 'lucide-react';
import { SupportedLanguage, ReadingLevel } from '../types';

interface LanguageSelectorProps {
  language: SupportedLanguage;
  readingLevel: ReadingLevel;
  onLanguageChange: (lang: SupportedLanguage) => void;
  onReadingLevelChange: (level: ReadingLevel) => void;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  language,
  readingLevel,
  onLanguageChange,
  onReadingLevelChange,
}) => {
  return (
    <div className="card no-print" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
      <div>
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>
          <Languages size={18} style={{ color: '#2563eb' }} />
          <span>Preferred Language</span>
        </label>
        <div style={{ display: 'flex', gap: '8px' }}>
          {(['English', 'Hindi', 'Kannada'] as SupportedLanguage[]).map((lang) => (
            <button
              key={lang}
              type="button"
              className={`btn ${language === lang ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1 }}
              onClick={() => onLanguageChange(lang)}
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>
          <BookOpen size={18} style={{ color: '#2563eb' }} />
          <span>Explanation Level</span>
        </label>
        <div style={{ display: 'flex', gap: '8px' }}>
          {(['Simple', 'Standard', 'Detailed'] as ReadingLevel[]).map((level) => (
            <button
              key={level}
              type="button"
              className={`btn ${readingLevel === level ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1 }}
              onClick={() => onReadingLevelChange(level)}
            >
              {level}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

