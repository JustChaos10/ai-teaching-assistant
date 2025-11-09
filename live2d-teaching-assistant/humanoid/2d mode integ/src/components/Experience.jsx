import React from 'react';

export function Experience({ audioUrl, phonemes }) {
  return (
    <div 
      style={{ 
        width: '100%', 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: '#e9eef7',  // Light text (matches inline theme)
        fontFamily: 'Inter, sans-serif',
        textAlign: 'center',
        padding: '20px',
        background: 'transparent'  // Inherits dark from app inline
      }}
    >
      <div>
        <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#e9eef7' }}>Live2D Teaching Assistant</h2>
        <p style={{ margin: '10px 0', color: '#a8b3c7' }}>Haru model will render here with lip-sync (Cubism SDK next)</p>
        <p style={{ margin: 5, color: '#e9eef7' }}>Audio Status: <span style={{ color: audioUrl ? '#2ecc71' : '#a8b3c7' }}>{audioUrl ? 'Playing' : 'Idle'}</span></p>
        <p style={{ margin: 5, color: '#e9eef7' }}>Phonemes: <span style={{ color: phonemes ? '#6aa7ff' : '#a8b3c7' }}>{phonemes ? `${phonemes.length} frames ready for sync` : 'Waiting for input'}</span></p>
      </div>
    </div>
  );
}
