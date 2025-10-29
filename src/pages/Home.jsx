import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home">
      {/* ---- Hero Section ---- */}
      <section className="hero">
        <h3 className="badge">Powered by AI & News Analytics</h3>
        <h1 className="title">
          Predict Disease Outbreaks <br /> with News Intelligence
        </h1>
        <p className="subtitle">
          EpiWatch analyzes global news sources using NLP and time-series analysis
          to identify emerging disease trends and predict potential outbreaks before
          they become widespread.
        </p>

        <div className="hero-buttons">
          <Link to="/analysis" className="btn primary">
            View Dashboard →
          </Link>
          <Link to="/data" className="btn secondary">
            Learn More
          </Link>
        </div>
      </section>

      {/* ---- Feature Grid ---- */}
      <section className="features">
        <div className="feature-card">
          <h3>🩺 Real-time Monitoring</h3>
          <p>Track disease mentions across global news sources.</p>
        </div>

        <div className="feature-card">
          <h3>🧠 NLP Analysis</h3>
          <p>Extract insights using advanced natural language processing.</p>
        </div>

        <div className="feature-card">
          <h3>📈 Predictive Analytics</h3>
          <p>Forecast disease trends using time-series analysis.</p>
        </div>

        <div className="feature-card">
          <h3>⚠️ Early Warning</h3>
          <p>Detect anomalies and emerging health threats early.</p>
        </div>
      </section>
    </div>
  );
}

export default Home;