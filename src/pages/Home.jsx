import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div>
      <h2>Welcome Home!</h2>
      <p>This is the landing page content.</p>
      <Link to="/about">Go to About Page</Link>
    </div>
  );
}

export default Home;