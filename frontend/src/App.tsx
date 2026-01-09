import React, { useState } from 'react';
import { EnrollmentFlow } from './components/EnrollmentFlow';
import { VerificationFlow } from './components/VerificationFlow';
import './App.css';

type View = 'enroll' | 'verify';

function App() {
  const [currentView, setCurrentView] = useState<View>('enroll');

  return (
    <div className="App">
      {currentView === 'enroll' && (
        <EnrollmentFlow onComplete={() => setCurrentView('verify')} />
      )}
      
      {currentView === 'verify' && (
        <VerificationFlow />
      )}
      
      {currentView === 'verify' && (
        <button
          onClick={() => setCurrentView('enroll')}
          className="back-button"
        >
          ← Back to Enrollment
        </button>
      )}
    </div>
  );
}

export default App;
