import React from 'react';
import { Link } from 'react-router-dom';

function Analysis() {
  return (
    <div>
      <h2>Analysis Page</h2>
      <p>This page will later display data analysis and model forecasts.</p>

      <div style={{ marginTop: '20px' }}>
        <Link to="/" style={{ marginRight: '15px' }}>Go to Home Page</Link>
        <Link to="/data">Go to Data Page</Link>
      </div>
    </div>
  );
}

export default Analysis;