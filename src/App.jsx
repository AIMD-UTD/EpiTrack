import React from 'react';
import { Outlet, Link } from 'react-router-dom'; // Import Link and Outlet

function App() {
  return (
    <div>
      {/* --- Global Navigation Bar --- */}
      <nav style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
        <Link to="/" style={{ marginRight: '15px' }}>Home</Link>
        <Link to="/about">About</Link>
      </nav>
      
      {/* --- Page Content (Renders Home or About page here) --- */}
      <main style={{ padding: '20px' }}>
        <Outlet />
      </main>
      
      {/* --- Global Footer --- */}
      <footer>
        <p>&copy; 2025 EpiTrack App</p>
      </footer>
    </div>
  );
}

export default App;