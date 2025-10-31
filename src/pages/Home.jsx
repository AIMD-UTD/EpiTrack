import { FiBarChart, FiActivity, FiAlertTriangle, FiCpu } from "react-icons/fi";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-indigo-600">EpiTrack</h1>
            </div>
            <div className="flex space-x-8">
              <a href="/" className="text-indigo-600 font-semibold">Home</a>
              <a href="/dashboard" className="text-gray-700 hover:text-indigo-600">Dashboard</a>
              <a href="/data-sources" className="text-gray-700 hover:text-indigo-600">Data Sources</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            Predict Disease Outbreaks with News Intelligence
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            EpiTrack analyzes global news sources using NLP and time series analysis to identify emerging disease trends and predict potential outbreaks before they become widespread.
          </p>
          
          <div className="flex justify-center space-x-4 mb-16">
            <a href="/dashboard" className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
              View Dashboard
            </a>
            <button className="border border-indigo-600 text-indigo-600 px-6 py-3 rounded-lg font-semibold hover:bg-indigo-50 transition">
              Learn More
            </button>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="text-blue-400 mb-3">
                <FiActivity size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-3">Real-time Monitoring</h3>
              <p className="text-gray-600">Track disease mentions across global news sources</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="text-blue-400 mb-3">
                <FiCpu size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-3">NLP Analysis</h3>
              <p className="text-gray-600">Extract insights using advanced natural language processing</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="text-blue-400 mb-3">
                <FiBarChart size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-3">Predictive Analytics</h3>
              <p className="text-gray-600">Forecast disease trends using time series analysis</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="text-blue-400 mb-3">
                <FiAlertTriangle size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-3">Early Warning</h3>
              <p className="text-gray-600">Detect anomalies and emerging health threats</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}