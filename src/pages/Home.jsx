// C:/Users/Deethya Janjanam/temp/EpiTrack/src/pages/Home.jsx

import React from 'react';
// Import your components once you create them
// import Header from '../components/Header';
// import MapContainer from '../components/MapContainer';
// import RealTimeMonitoring from '../components/RealTimeMonitoring';
// import FooterWidgets from '../components/FooterWidgets';

const Home = () => {
  return (
    <div className="home-screen">
      
      {/* 1. Header Section */}
      <header className="app-header">
        <h1>EpiTrack</h1>
      </header>
      
      {/* 2. Hero Section / Tagline */}
      <section className="hero-section">
        <h2>Predict Disease Outbreaks Before They Spread</h2>
      </section>

      {/* 3. Map and Outbreak Information (The main middle section) */}
      <section className="map-and-info-section">
        <div className="map-area">
          {/* Component for the map visualization goes here */}
        </div>
        <aside className="outbreak-info-card">
          <h4>Outbreak Information</h4>
          {/* List of stats (Total Outbreaks, Infected Cases, etc.) */}
        </aside>
      </section>

      {/* 4. Real-Time Monitoring Chart Section */}
      <section className="monitoring-section">
        <h3>Real Time Monitoring</h3>
        <div className="chart-container">
          {/* Component for the Line Chart goes here */}
        </div>
      </section>

      {/* 5. Footer Widgets (News and Regions) */}
      <section className="widgets-section">
        <div className="news-feed-widget">
          {/* Content for the News Feed */}
        </div>
        <div className="regions-widget">
          {/* Content for Regions with most cases */}
        </div>
      </section>
{/*hello*/}
    </div>
  );
};

export default Home;