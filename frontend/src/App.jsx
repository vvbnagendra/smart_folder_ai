import React, { useState, useEffect } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('keyword');
  const [results, setResults] = useState([]);
  const [faceClusters, setFaceClusters] = useState([]);
  const [scanStatus, setScanStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [systemStats, setSystemStats] = useState(null);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [clusterImages, setClusterImages] = useState([]);
  
  // New state for folder selection
  const [defaultPaths, setDefaultPaths] = useState([]);
  const [selectedPaths, setSelectedPaths] = useState([]);
  const [customPath, setCustomPath] = useState('');
  const [showPathSelector, setShowPathSelector] = useState(false);

  // Fetch initial data on mount
  useEffect(() => {
    fetchSystemStatus();
    fetchFaceClusters();
    fetchDefaultPaths();
  }, []);

  const fetchDefaultPaths = async () => {
    try {
      const response = await fetch('/api/default-paths');
      const data = await response.json();
      setDefaultPaths(data);
      // Set initial selected paths from available defaults
      const availablePaths = data.default_paths
        .filter(p => p.exists && p.readable)
        .map(p => p.path);
      setSelectedPaths(availablePaths.slice(0, 2)); // Select first 2 by default
    } catch (error) {
      console.error('Error fetching default paths:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const fetchFaceClusters = async () => {
    try {
      const response = await fetch('/api/faces');
      const data = await response.json();
      setFaceClusters(data);
    } catch (error) {
      console.error('Error fetching face clusters:', error);
    }
  };

  const fetchClusterImages = async (clusterId) => {
    try {
      const response = await fetch(`/api/faces/${clusterId}`, { method: 'POST' });
      const data = await response.json();
      setClusterImages(data.images || []);
      setSelectedCluster(clusterId);
    } catch (error) {
      console.error('Error fetching cluster images:', error);
    }
  };

  const handleScan = async () => {
    if (selectedPaths.length === 0) {
      alert('Please select at least one folder to scan.');
      return;
    }

    setLoading(true);
    setScanStatus(null);
    try {
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paths: selectedPaths })
      });
      const data = await response.json();
      setScanStatus(data);
      // Refresh data after scan
      fetchFaceClusters();
      fetchSystemStatus();
    } catch (error) {
      console.error('Error starting scan:', error);
      setScanStatus({ status: 'Error: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setResults([]);
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), search_type: searchType }),
      });
      const data = await response.json();
      setResults(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error performing search:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const addCustomPath = () => {
    if (customPath.trim() && !selectedPaths.includes(customPath.trim())) {
      setSelectedPaths([...selectedPaths, customPath.trim()]);
      setCustomPath('');
    }
  };

  const removePath = (pathToRemove) => {
    setSelectedPaths(selectedPaths.filter(path => path !== pathToRemove));
  };

  const togglePath = (path) => {
    if (selectedPaths.includes(path)) {
      removePath(path);
    } else {
      setSelectedPaths([...selectedPaths, path]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileTypeIcon = (fileType) => {
    const icons = {
      image: '🖼️',
      document: '📄',
      text: '📝',
      video: '🎬',
      audio: '🎵',
      unknown: '📁'
    };
    return icons[fileType] || icons.unknown;
  };

  const getOSIcon = (os) => {
    const icons = {
      'Windows': '🪟',
      'Darwin': '🍎',
      'Linux': '🐧'
    };
    return icons[os] || '💻';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">Smart Folder Organizer</h1>
          <p className="text-blue-100 mt-2">AI-powered file management and search</p>
          
          {/* System Status */}
          <div className="mt-4 flex flex-wrap gap-4 text-sm">
            {systemStats && (
              <>
                <span className="bg-blue-500 px-3 py-1 rounded flex items-center gap-1">
                  {getOSIcon(systemStats.os)} {systemStats.os}
                </span>
                <span className="bg-blue-500 px-3 py-1 rounded">
                  📁 {systemStats.total_files} files
                </span>
                <span className="bg-blue-500 px-3 py-1 rounded">
                  🔍 {systemStats.indexed_files} indexed
                </span>
                <span className="bg-blue-500 px-3 py-1 rounded">
                  👥 {systemStats.face_clusters} face clusters
                </span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Folder Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">📂 Select Folders to Scan</h2>
              <p className="text-gray-600">Choose which directories to scan for files and content.</p>
            </div>
            <button
              onClick={() => setShowPathSelector(!showPathSelector)}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              {showPathSelector ? '📁 Hide Folders' : '📁 Manage Folders'}
            </button>
          </div>

          {/* Selected Paths Display */}
          <div className="mb-4">
            <h3 className="font-medium mb-2">Selected Folders ({selectedPaths.length}):</h3>
            {selectedPaths.length > 0 ? (
              <div className="space-y-2">
                {selectedPaths.map((path, index) => (
                  <div key={index} className="flex items-center justify-between bg-green-50 border border-green-200 rounded p-3">
                    <span className="font-mono text-sm text-green-800">📁 {path}</span>
                    <button
                      onClick={() => removePath(path)}
                      className="text-red-600 hover:text-red-800 ml-2"
                      title="Remove folder"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-yellow-600 bg-yellow-50 border border-yellow-200 rounded p-3">
                ⚠️ No folders selected. Please select folders to scan.
              </p>
            )}
          </div>

          {/* Folder Selection UI */}
          {showPathSelector && (
            <div className="border-t pt-4">
              {/* Default/Suggested Paths */}
              {defaultPaths.default_paths && (
                <div className="mb-6">
                  <h3 className="font-medium mb-3">💡 Suggested Folders:</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {defaultPaths.default_paths.map((pathInfo, index) => (
                      <div key={index} className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                        selectedPaths.includes(pathInfo.path) 
                          ? 'border-green-500 bg-green-50' 
                          : pathInfo.exists && pathInfo.readable
                            ? 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                            : 'border-red-300 bg-red-50'
                      }`}>
                        <div 
                          onClick={() => pathInfo.exists && pathInfo.readable && togglePath(pathInfo.path)}
                          className="flex items-center justify-between"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className={`w-4 h-4 rounded ${
                                selectedPaths.includes(pathInfo.path) ? 'bg-green-500' : 'bg-gray-300'
                              }`}></span>
                              <span className="font-mono text-sm">{pathInfo.path}</span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {pathInfo.exists 
                                ? pathInfo.readable 
                                  ? `~${formatFileSize(pathInfo.size_estimate)}`
                                  : '❌ Not readable'
                                : '❌ Does not exist'
                              }
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Common Folders */}
              {defaultPaths.common_folders && defaultPaths.common_folders.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-medium mb-3">🎯 Common Folders:</h3>
                  <div className="flex flex-wrap gap-2">
                    {defaultPaths.common_folders.map((path, index) => (
                      <button
                        key={index}
                        onClick={() => togglePath(path)}
                        className={`px-3 py-1 rounded text-sm transition-colors ${
                          selectedPaths.includes(path)
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {selectedPaths.includes(path) ? '✓ ' : '+ '}{path.split('/').pop() || path.split('\\').pop()}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Custom Path Input */}
              <div>
                <h3 className="font-medium mb-3">✏️ Add Custom Folder:</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customPath}
                    onChange={(e) => setCustomPath(e.target.value)}
                    placeholder={defaultPaths.os === 'Windows' ? 'C:\\Users\\YourName\\CustomFolder' : '/home/user/customfolder'}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  />
                  <button
                    onClick={addCustomPath}
                    disabled={!customPath.trim()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                  >
                    Add
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {defaultPaths.os === 'Windows' 
                    ? 'Example: C:\\Users\\YourName\\Documents'
                    : 'Example: /home/user/documents'
                  }
                </p>
              </div>
            </div>
          )}

          {/* Scan Button */}
          <div className="flex justify-center mt-6">
            <button
              onClick={handleScan}
              disabled={loading || selectedPaths.length === 0}
              className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-medium text-lg"
            >
              {loading ? '⏳ Scanning...' : '🚀 Start Scan'}
            </button>
          </div>
          
          {scanStatus && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium">
                Status: {scanStatus.status}
              </p>
              {scanStatus.total_files && (
                <div className="mt-2 text-green-700 text-sm space-y-1">
                  <p>📊 Total files: {scanStatus.total_files}</p>
                  <p>✅ Indexed: {scanStatus.indexed_files}</p>
                  <p>🎯 Vector indexed: {scanStatus.vector_indexed}</p>
                  <p>📂 Scanned paths: {scanStatus.scan_paths?.join(', ')}</p>
                  {scanStatus.file_types && (
                    <div className="mt-2">
                      <strong>File types:</strong>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {Object.entries(scanStatus.file_types).map(([type, count]) => (
                          <span key={type} className="bg-green-100 px-2 py-1 rounded text-xs">
                            {getFileTypeIcon(type)} {type}: {count}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Search Interface */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">🔍 Search Files</h2>
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for files, content, or keywords..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>
            
            <div className="flex gap-6">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="keyword"
                  checked={searchType === 'keyword'}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="mr-2"
                />
                🔤 Keyword Search
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="semantic"
                  checked={searchType === 'semantic'}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="mr-2"
                />
                🧠 Semantic Search
              </label>
            </div>
            
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-medium"
            >
              {loading ? '⏳ Searching...' : '🔍 Search'}
            </button>
          </form>

          {/* Search Results */}
          {results.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">
                📋 Results ({results.length})
              </h3>
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{getFileTypeIcon(result.file_type)}</span>
                          <h4 className="font-medium text-blue-600 text-lg">{result.filename}</h4>
                          {result.size > 0 && (
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {formatFileSize(result.size)}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2 font-mono">📁 {result.path}</p>
                        {result.snippet && (
                          <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded italic">
                            "{result.snippet}"
                          </p>
                        )}
                      </div>
                      {(result.score || result.relevance) && (
                        <div className="ml-4 text-right">
                          <div className="text-xs text-gray-500">Relevance</div>
                          <div className="text-sm font-bold text-blue-600">
                            {((result.score || result.relevance) * 100).toFixed(1)}%
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {results.length === 0 && query && !loading && (
            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800">No results found for "{query}". Try different keywords or run a scan first.</p>
            </div>
          )}
        </div>

        {/* Face Clusters */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">👥 Face Recognition</h2>
          
          {faceClusters.length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {faceClusters.map((cluster) => (
                  <div 
                    key={cluster.cluster_id} 
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => fetchClusterImages(cluster.cluster_id)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex-shrink-0">
                        {cluster.thumbnail ? (
                          <img 
                            src={cluster.thumbnail} 
                            alt={`Person ${cluster.cluster_id}`}
                            className="w-16 h-16 rounded-full object-cover border-2 border-blue-200"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-600 font-bold text-lg">
                              {cluster.cluster_id}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-lg">{cluster.name}</h3>
                        <p className="text-sm text-gray-600">{cluster.count} photos</p>
                        {cluster.sample_images && (
                          <p className="text-xs text-gray-500 mt-1">
                            Click to view all images
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Cluster Images Modal */}
              {selectedCluster && clusterImages.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">
                      Images for Person {selectedCluster}
                    </h3>
                    <button 
                      onClick={() => {setSelectedCluster(null); setClusterImages([]);}}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      ✕ Close
                    </button>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                    {clusterImages.map((image, index) => (
                      <div key={index} className="aspect-square">
                        {image.thumbnail ? (
                          <img 
                            src={image.thumbnail}
                            alt={`Face ${index + 1}`}
                            className="w-full h-full object-cover rounded border"
                          />
                        ) : (
                          <div className="w-full h-full bg-gray-200 rounded border flex items-center justify-center">
                            <span className="text-gray-500 text-xs">No thumb</span>
                          </div>
                        )}
                        <p className="text-xs text-gray-600 mt-1 truncate" title={image.path}>
                          {image.path ? image.path.split(/[/\\]/).pop() : 'Unknown'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">👤</div>
              <p className="text-gray-500 text-lg">No face clusters detected yet.</p>
              <p className="text-gray-400 mt-2">Run a scan to detect and group faces in your images.</p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <p>Smart Folder Organizer - Powered by AI</p>
            {systemStats && (
              <p className="text-sm text-gray-400">
                System: {systemStats.status} | Files: {systemStats.total_files} | OS: {systemStats.os}
              </p>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;