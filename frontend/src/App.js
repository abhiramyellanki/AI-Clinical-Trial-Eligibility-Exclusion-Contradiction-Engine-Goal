import React from 'react';
import EligibilityForm from './components/EligibilityForm'; // Import the main form component
import './index.css'; // Import global styles (including Tailwind)

function App() {
  return (
    <div className="App">
      {/* Render the EligibilityForm component. 
        It contains the entire UI: inputs, button, loading state, and results display.
      */}
      <EligibilityForm />
    </div>
  );
}

export default App;