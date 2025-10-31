export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-indigo-600">EpiTrack</h1>
            </div>
            <div className="flex space-x-8">
              <a href="/" className="text-gray-700 hover:text-indigo-600">Home</a>
              <a href="/dashboard" className="text-indigo-600 font-semibold">Dashboard</a>
              <a href="/data-sources" className="text-gray-700 hover:text-indigo-600">Data Sources</a>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Disease Prediction Dashboard</h1>
          <p className="text-gray-600">Real-time insights and predictions based on global news analysis</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Active Diseases</h3>
            <p className="text-2xl font-bold text-gray-900">5</p>
            <p className="text-sm text-gray-500">Being monitored</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Rising Trends</h3>
            <p className="text-2xl font-bold text-gray-900">5</p>
            <p className="text-sm text-gray-500">Diseases increasing</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Alert Level</h3>
            <p className="text-2xl font-bold text-green-600">Low</p>
            <p className="text-sm text-gray-500">2 anomalies</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Data Points</h3>
            <p className="text-2xl font-bold text-gray-900">60</p>
            <p className="text-sm text-gray-500">10/31/2024 - 9/30/2025</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Analysis Tools */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">Analysis Tools</h2>
              <div className="space-y-3">
                {['Trends', 'Predictions', 'Sentiment', 'Patterns', 'Correlations', 'US Map'].map((tool) => (
                  <button key={tool} className="w-full text-left px-4 py-2 rounded-lg hover:bg-indigo-50 text-gray-700 hover:text-indigo-600 transition">
                    {tool}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Disease Trends */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">Disease Trend Analysis</h2>
              <p className="text-gray-600 mb-6">Current trends and trajectories for monitored diseases</p>
              
              {/* Disease List */}
              <div className="flex flex-wrap gap-2 mb-6">
                {['Malaria', 'Covid', 'Tuberculosis', 'Dengue', 'Influenza'].map((disease) => (
                  <span key={disease} className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-700">
                    {disease}
                  </span>
                ))}
              </div>

              {/* Chart Placeholder */}
              <div className="bg-gray-50 rounded-lg p-8 mb-4">
                <div className="h-64 flex items-end justify-between space-x-2">
                  {/* Chart bars placeholder */}
                  {[60, 45, 80, 30, 70, 55, 40, 85].map((height, index) => (
                    <div key={index} className="flex flex-col items-center flex-1">
                      <div 
                        className="w-full bg-indigo-500 rounded-t transition-all duration-300 max-w-12"
                        style={{ height: `${height}%` }}
                      ></div>
                      <span className="text-xs text-gray-500 mt-2">D{index + 1}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="text-center text-sm text-gray-500">
                10/20/2025 ~ covid ~ dengue ~ influenza ~ malaria ~ tuberculosis
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}