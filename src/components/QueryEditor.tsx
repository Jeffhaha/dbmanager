import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play } from 'lucide-react';

interface Database {
  id: number;
  name: string;
  type: string;
  status: string;
}

interface DatabaseSchema {
  [tableName: string]: string[];
}

const QueryEditor: React.FC = () => {
  const [databases, setDatabases] = useState<Database[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<number | null>(null);
  const [databaseSchema, setDatabaseSchema] = useState<DatabaseSchema | null>(null);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[] | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatabases();
  }, []);

  useEffect(() => {
    if (selectedDatabase) {
      fetchDatabaseSchema(selectedDatabase);
    }
  }, [selectedDatabase]);

  const fetchDatabases = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/databases', { withCredentials: true });
      setDatabases(response.data);
      const connectedDb = response.data.find((db: Database) => db.status === 'Connected');
      if (connectedDb) {
        setSelectedDatabase(connectedDb.id);
      }
    } catch (error) {
      console.error('Error fetching databases:', error);
      setError('Failed to fetch databases. Please try again.');
    }
  };

  const fetchDatabaseSchema = async (dbId: number) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/database-schema/${dbId}`, { withCredentials: true });
      setDatabaseSchema(response.data);
    } catch (error) {
      console.error('Error fetching database schema:', error);
      if (axios.isAxiosError(error)) {
        console.error('Response data:', error.response?.data);
        console.error('Response status:', error.response?.status);
      }
      setError('Failed to fetch database schema. Please try again.');
    }
  };

  const handleExecuteQuery = async () => {
    if (!selectedDatabase) {
      setError('Please select a database');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:5000/api/execute-query', { 
        databaseId: selectedDatabase, 
        query 
      }, { withCredentials: true });
      setColumns(response.data.columns);
      setResults(response.data.rows);
    } catch (error: any) {
      console.error('Error executing query:', error);
      setError(error.response?.data?.error || 'An error occurred while executing the query. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTableSelect = (tableName: string) => {
    setSelectedTable(tableName);
    setQuery(`SELECT * FROM ${tableName} LIMIT 10;`);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Query Editor</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-1">
          <h2 className="text-xl font-semibold mb-2">Databases</h2>
          <select
            className="w-full p-2 border rounded"
            value={selectedDatabase || ''}
            onChange={(e) => setSelectedDatabase(Number(e.target.value))}
          >
            <option value="">Select a database</option>
            {databases.map((db) => (
              <option key={db.id} value={db.id}>
                {db.name} ({db.type}) - {db.status}
              </option>
            ))}
          </select>

          {databaseSchema && (
            <div className="mt-4">
              <h2 className="text-xl font-semibold mb-2">Tables</h2>
              <ul className="max-h-64 overflow-y-auto border rounded p-2">
                {Object.keys(databaseSchema).map((tableName) => (
                  <li
                    key={tableName}
                    className={`cursor-pointer p-1 hover:bg-gray-100 ${selectedTable === tableName ? 'bg-blue-100' : ''}`}
                    onClick={() => handleTableSelect(tableName)}
                  >
                    {tableName}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {selectedTable && databaseSchema && (
            <div className="mt-4">
              <h2 className="text-xl font-semibold mb-2">Columns</h2>
              <ul className="max-h-64 overflow-y-auto border rounded p-2">
                {databaseSchema[selectedTable].map((columnName) => (
                  <li key={columnName} className="p-1">
                    {columnName}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="col-span-3">
          <textarea
            className="w-full h-40 p-2 border rounded mb-4"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your SQL query here..."
          />
          <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded inline-flex items-center"
            onClick={handleExecuteQuery}
            disabled={isLoading}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <Play className="w-4 h-4 mr-2" />
            )}
            {isLoading ? 'Executing...' : 'Execute Query'}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}

          {results && (
            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-2">Query Results</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border rounded-lg">
                  <thead className="bg-gray-100">
                    <tr>
                      {columns.map((column) => (
                        <th key={column} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {results.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {columns.map((column) => (
                          <td key={`${rowIndex}-${column}`} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {row[column] !== null ? row[column].toString() : 'NULL'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QueryEditor;
