export default function DataSources() {
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
              <a href="/dashboard" className="text-gray-700 hover:text-indigo-600">Dashboard</a>
              <a href="/data-sources" className="text-indigo-600 font-semibold">Data Sources</a>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Data Sources & Collection</h1>
          <p className="text-gray-600">Comprehensive news data collection and processing pipeline</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-xl shadow-sm text-center">
            <h3 className="text-2xl font-bold text-indigo-600 mb-2">1.2M+</h3>
            <p className="text-gray-600">Articles Processed</p>
            <p className="text-sm text-gray-500">Total articles analyzed</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm text-center">
            <h3 className="text-2xl font-bold text-indigo-600 mb-2">45K+</h3>
            <p className="text-gray-600">Keywords Extracted</p>
            <p className="text-sm text-gray-500">Unique health-related terms</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm text-center">
            <h3 className="text-2xl font-bold text-indigo-600 mb-2">50+</h3>
            <p className="text-gray-600">Diseases Tracked</p>
            <p className="text-sm text-gray-500">Active disease categories</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm text-center">
            <h3 className="text-2xl font-bold text-indigo-600 mb-2">195</h3>
            <p className="text-gray-600">Countries Covered</p>
            <p className="text-sm text-gray-500">Global news coverage</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Data Sources Section */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Data Sources</h2>
            <p className="text-gray-600 mb-6">Active news sources and data feeds</p>
            
            <div className="space-y-4">
              {[
                { name: 'News API', status: 'Active', description: 'Global news articles from 70,000+ sources', coverage: 'Worldwide' },
                { name: 'Health Headlines', status: 'Active', description: 'Created health and medical news', coverage: 'Medical Focus' },
                { name: 'Real-time Feed', status: 'Active', description: 'Live updates from breaking news', coverage: '24/7 Monitoring' }
              ].map((source, index) => (
                <div key={index} className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg">
                  <input type="checkbox" defaultChecked className="mt-1 rounded text-indigo-600" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-gray-900">{source.name}</h3>
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">{source.status}</span>
                    </div>
                    <p className="text-gray-600 text-sm mt-1">{source.description}</p>
                    <p className="text-gray-500 text-xs mt-1">Coverage: {source.coverage}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Search Section */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">News Data Collection</h2>
            <p className="text-gray-600 mb-6">
              Fetch health-related news articles for disease trend analysis
            </p>
            
            <div className="space-y-4">
              <div className="relative">
                <input 
                  type="text" 
                  placeholder="Search for disease or health topic..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <button className="absolute right-2 top-2 bg-indigo-600 text-white px-4 py-1 rounded-md hover:bg-indigo-700 transition">
                  Search
                </button>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-medium mb-3 text-gray-900">Recent Searches</h3>
                <div className="space-y-2">
                  {['Influenza outbreak', 'Malaria prevention', 'COVID variants', 'Dengue fever'].map((search, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-0">
                      <span className="text-gray-700">{search}</span>
                      <span className="text-xs text-gray-500">2h ago</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}