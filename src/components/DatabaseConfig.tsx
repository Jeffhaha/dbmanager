import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Lock } from 'lucide-react';

interface Database {
  id: number;
  name: string;
  type: string;
  host: string;
  port: string;
  user: string;
  password: string;
  database: string;
  status: string;
}

interface DatabaseConfigProps {
  databaseId: number;
  onClose: () => void;
}

const DatabaseConfig: React.FC<DatabaseConfigProps> = ({ databaseId, onClose }) => {
  const [database, setDatabase] = useState<Database>({
    id: 0,
    name: '',
    type: '',
    host: '',
    port: '',
    user: '',
    password: '',
    database: '',
    status: 'Disconnected',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatabaseDetails();
  }, [databaseId]);

  const fetchDatabaseDetails = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/databases/${databaseId}`);
      setDatabase(response.data);
    } catch (error) {
      console.error('Error fetching database details:', error);
      setError('Failed to fetch database details. Please try again.');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setDatabase({ ...database, [name]: value });
  };

  const handleTestConnection = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(`http://localhost:5000/api/databases/${databaseId}/test`, database, { withCredentials: true });
      alert(response.data.message);
      setDatabase(prevState => ({ ...prevState, status: response.data.status }));
    } catch (error: any) {
      console.error('Error testing connection:', error);
      setError(error.response?.data?.error || 'Failed to test connection. Please check your configuration and try again.');
      setDatabase(prevState => ({ ...prevState, status: 'Disconnected' }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await axios.put(`http://localhost:5000/api/databases/${databaseId}`, database, { withCredentials: true });
      onClose();
    } catch (error: any) {
      console.error('Error saving database configuration:', error);
      setError(error.response?.data?.error || 'Failed to save database configuration. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h2 className="text-lg font-semibold mb-4">Configure Database Connection</h2>
        <form>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
              Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={database.name}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="type">
              Type
            </label>
            <input
              type="text"
              id="type"
              name="type"
              value={database.type}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="host">
              Host
            </label>
            <input
              type="text"
              id="host"
              name="host"
              value={database.host}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="port">
              Port
            </label>
            <input
              type="text"
              id="port"
              name="port"
              value={database.port}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="user">
              User
            </label>
            <input
              type="text"
              id="user"
              name="user"
              value={database.user}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                id="password"
                name="password"
                value={database.password}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline pr-10"
              />
              <Lock className="absolute right-3 top-2 h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="database">
              Database
            </label>
            <input
              type="text"
              id="database"
              name="database"
              value={database.database}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="status">
              Status
            </label>
            <input
              type="text"
              id="status"
              name="status"
              value={database.status}
              readOnly
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={handleTestConnection}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={isLoading}
            >
              Test Connection
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={isLoading}
            >
              Save
            </button>
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DatabaseConfig;
