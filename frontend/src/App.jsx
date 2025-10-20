import React, { useState, useEffect } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('keyword');
  const [results, setResults] = useState([]);
  const [faceClusters, setFaceClusters] = useState([]);
  const [scanStatus, setScanStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch face clusters on mount
  useEffect(() => {
    fetchFaceClusters();
  }, []);

  const fetchFaceClusters = async () => {
    try {
      const response = await fetch('/api/faces');
      const data = await response.json();
      setFaceClusters(data);
    } catch (error) {
      console.error('Error fetching face clusters:', error);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/scan', { method: 'POST' });
      const data = await response.json();
      setScanStatus(data);
      fetchFaceClusters(); // Refresh face clusters after scan
    } catch (error) {
      console.error('Error starting scan:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, search_type: searchType }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error performing search:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">Smart Folder Organizer</h1>
          <p className="text-blue-100 mt-2">AI-powered file management and search</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Scan Control */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Scan & Index</h2>
          <button
            onClick={handleScan}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {loading ? 'Scanning...' : 'Start Scan'}
          </button>
          {scanStatus && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800">
                <strong>Status:</strong> {scanStatus.status}
              </p>
              {scanStatus.total_files && (
                <p className="text-green-700 mt-1">
                  Total files indexed: {scanStatus.total_files}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Search Interface */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Search Files</h2>
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for files, content, or faces..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="keyword"
                  checked={searchType === 'keyword'}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="mr-2"
                />
                Keyword Search
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="semantic"
                  checked={searchType === 'semantic'}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="mr-2"
                />
                Semantic Search
              </label>
            </div>
            <button
              type="submit"
              disabled={loading || !query}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
            >
              Search
            </button>
          </form>

          {/* Search Results */}
          {results.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Results ({results.length})</h3>
              <div className="space-y-3">
                {results.map((result, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <h4 className="font-medium text-blue-600">{result.filename}</h4>
                    <p className="text-sm text-gray-600 mt-1">{result.path}</p>
                    {result.snippet && (
                      <p className="text-sm text-gray-700 mt-2 italic">{result.snippet}</p>
                    )}
                    {result.score && (
                      <p className="text-xs text-gray-500 mt-1">Relevance: {(result.score * 100).toFixed(1)}%</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Face Clusters */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Face Clusters</h2>
          {faceClusters.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {faceClusters.map((cluster) => (
                <div key={cluster.cluster_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{cluster.name}</h3>
                      <p className="text-sm text-gray-600">{cluster.count} photos</p>
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-bold">{cluster.cluster_id}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No face clusters detected yet. Run a scan to detect faces.</p>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>Smart Folder Organizer - Powered by AI</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

