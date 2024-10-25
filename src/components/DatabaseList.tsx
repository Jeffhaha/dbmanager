import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, Settings } from 'lucide-react';
import DatabaseConfig from './DatabaseConfig';

interface DatabaseConnection {
  id: number;
  name: string;
  type: string;
  status: string;
}

const DatabaseList: React.FC = () => {
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [selectedDatabaseId, setSelectedDatabaseId] = useState<number | null>(null);

  useEffect(() => {
    fetchDatabases();
    const intervalId = setInterval(fetchDatabases, 5000);
    return () => clearInterval(intervalId);
  }, []);

  const fetchDatabases = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/databases');
      setDatabases(response.data);
    } catch (error) {
      console.error('Error fetching databases:', error);
    }
  };

  const handleConfigureClick = (id: number) => {
    setSelectedDatabaseId(id);
  };

  const handleCloseConfig = () => {
    setSelectedDatabaseId(null);
    fetchDatabases();
  };

  const handleToggleConnection = async (id: number) => {
    try {
      const response = await axios.post(`http://localhost:5000/api/databases/${id}/toggle`);
      fetchDatabases();
    } catch (error) {
      console.error('Error toggling database connection:', error);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Database Connections</h1>
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {databases.map((db) => (
              <tr key={db.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Database className="w-5 h-5 mr-2 text-gray-500" />
                    <div className="text-sm font-medium text-gray-900">{db.name}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{db.type}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleToggleConnection(db.id)}
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      db.status === 'Connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {db.status}
                  </button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    className="text-indigo-600 hover:text-indigo-900 mr-2"
                    onClick={() => handleConfigureClick(db.id)}
                  >
                    <Settings className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selectedDatabaseId && (
        <DatabaseConfig databaseId={selectedDatabaseId} onClose={handleCloseConfig} />
      )}
    </div>
  );
};

export default DatabaseList;
