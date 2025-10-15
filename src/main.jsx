import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.jsx'; // <--- Now imports the main layout file
import Home from './pages/Home.jsx';
import About from './pages/About.jsx';

// Define the Router structure
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* The Route for the main layout uses the element={<App />} */}
        <Route path="/" element={<App />}> 
          
          {/* These child routes render inside the <Outlet /> within App.jsx */}
          <Route index element={<Home />} /> 
          <Route path="about" element={<About />} /> 
          
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);