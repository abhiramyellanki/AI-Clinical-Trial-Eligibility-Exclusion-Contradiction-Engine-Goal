import React from 'react';
import { createRoot } from 'react-dom/client'; // Use createRoot for React 18+
import App from './App';
import './index.css'; // Ensure Tailwind styles are loaded

const container = document.getElementById('root');
const root = createRoot(container); // Create a root

// Render the App component inside the root
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);