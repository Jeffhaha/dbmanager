import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Database, Home, Settings, Upload } from 'lucide-react';
import Dashboard from './components/Dashboard';
import DatabaseList from './components/DatabaseList';
import QueryEditor from './components/QueryEditor';
import FileUpload from './components/FileUpload';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100 flex">
        {/* Sidebar */}
        <nav className="bg-gray-800 text-white w-64 space-y-6 py-7 px-2">
          <div className="flex items-center space-x-2 px-4">
            <Database className="w-8 h-8" />
            <span className="text-2xl font-extrabold">DB Studio</span>
          </div>
          <ul className="space-y-2">
            <li>
              <Link to="/" className="flex items-center space-x-2 py-2 px-4 hover:bg-gray-700 rounded">
                <Home className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
            </li>
            <li>
              <Link to="/databases" className="flex items-center space-x-2 py-2 px-4 hover:bg-gray-700 rounded">
                <Database className="w-5 h-5" />
                <span>Databases</span>
              </Link>
            </li>
            <li>
              <Link to="/query" className="flex items-center space-x-2 py-2 px-4 hover:bg-gray-700 rounded">
                <Settings className="w-5 h-5" />
                <span>Query Editor</span>
              </Link>
            </li>
            <li>
              <Link to="/upload" className="flex items-center space-x-2 py-2 px-4 hover:bg-gray-700 rounded">
                <Upload className="w-5 h-5" />
                <span>File Upload</span>
              </Link>
            </li>
          </ul>
        </nav>

        {/* Main content */}
        <main className="flex-1 p-10">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/databases" element={<DatabaseList />} />
            <Route path="/query" element={<QueryEditor />} />
            <Route path="/upload" element={<FileUpload />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;