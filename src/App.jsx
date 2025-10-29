import React from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import "./App.css";

function App() {
  const location = useLocation();

  return (
    <div>
      {/* ---- Navbar ---- */}
      <header className="navbar">
        <div className="nav-left">
          <h2 className="logo">EpiWatch</h2>
        </div>

        <nav className="nav-center">
          <Link
            to="/"
            className={`nav-link ${location.pathname === "/" ? "active" : ""}`}
          >
            Dashboard
          </Link>
          <Link
            to="/analysis"
            className={`nav-link ${
              location.pathname === "/analysis" ? "active" : ""
            }`}
          >
            Analysis
          </Link>
          <Link
            to="/data"
            className={`nav-link ${
              location.pathname === "/data" ? "active" : ""
            }`}
          >
            Data
          </Link>
        </nav>

        <div className="nav-right">
          <Link to="/" className="btn-get-started">
            Get Started
          </Link>
        </div>
      </header>

      {/* ---- Page Content ---- */}
      <main className="main-content">
        <Outlet />
      </main>

      {/* ---- Footer ---- */}
      <footer className="footer">
        <p>&copy; 2025 EpiTrack App</p>
      </footer>
    </div>
  );
}

export default App;