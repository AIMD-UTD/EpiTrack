import React from 'react';
import { Link } from 'react-router-dom';

function About() {
  return (
    <div>
      <h2>About Us</h2>
      <p>Details about the EpiTrack project.</p>
      <Link to="/">Go back Home</Link>
    </div>
  );
}

export default About;