import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.jsx';
import Home from './pages/Home.jsx';
import Analysis from './pages/Analysis.jsx';
import Data from './pages/Data.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Home />} />
          <Route path="analysis" element={<Analysis />} />
          <Route path="data" element={<Data />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);