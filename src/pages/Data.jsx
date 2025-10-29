import React from 'react';
import { Link } from 'react-router-dom';

function Data() {
  return (
    <div>
      <h2>Data Page</h2>
      <p>This page will later show raw and processed datasets.</p>

      <div style={{ marginTop: '20px' }}>
        <Link to="/" style={{ marginRight: '15px' }}>Go to Home Page</Link>
        <Link to="/analysis">Go to Analysis Page</Link>
      </div>
    </div>
  );
}

export default Data;