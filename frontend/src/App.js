import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Use relative API URL since frontend and backend are served from same domain
const API_BASE_URL = '';

function App() {
  const [inputText, setInputText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [barcodes, setBarcodes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch all barcodes on component mount
  useEffect(() => {
    fetchBarcodes();
  }, []);

  const fetchBarcodes = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/barcodes`);
      setBarcodes(response.data.barcodes);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden der Barcodes');
      console.error('Error fetching barcodes:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const generateBarcode = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      setError('Bitte geben Sie Text oder Zahlen ein');
      return;
    }

    try {
      setIsGenerating(true);
      setError('');
      
      const response = await axios.post(`${API_BASE_URL}/api/generate-barcode`, {
        text: inputText.trim()
      });

      // Add new barcode to the beginning of the list
      setBarcodes(prev => [response.data, ...prev]);
      setInputText('');
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Fehler beim Generieren des Barcodes');
      console.error('Error generating barcode:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const deleteBarcode = async (barcodeId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/barcode/${barcodeId}`);
      setBarcodes(prev => prev.filter(barcode => barcode.id !== barcodeId));
    } catch (err) {
      setError('Fehler beim Löschen des Barcodes');
      console.error('Error deleting barcode:', err);
    }
  };

  const downloadBarcode = (barcode) => {
    const link = document.createElement('a');
    link.href = barcode.barcode_image;
    link.download = `barcode-${barcode.text}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('de-DE');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            <span className="text-indigo-600">Code128</span> Barcode Generator
          </h1>
          <p className="text-gray-600">Erstellen Sie Code128 Barcodes aus Text und Zahlen</p>
          <div className="mt-2">
            <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
              🚀 Kostenlos auf Render gehostet
            </span>
          </div>
        </div>

        {/* Generator Form */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <form onSubmit={generateBarcode} className="space-y-4">
              <div>
                <label htmlFor="inputText" className="block text-sm font-medium text-gray-700 mb-2">
                  Text oder Nummern eingeben
                </label>
                <input
                  type="text"
                  id="inputText"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="z.B. Hello World oder 123456789"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                  disabled={isGenerating}
                />
              </div>
              
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isGenerating || !inputText.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generiere Barcode...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    Barcode Generieren
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Barcodes List */}
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Generierte Barcodes</h2>
            <button
              onClick={fetchBarcodes}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              Aktualisieren
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <p className="mt-4 text-gray-600">Lade Barcodes...</p>
            </div>
          ) : barcodes.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">📊</div>
              <p className="text-gray-600">Noch keine Barcodes generiert</p>
              <p className="text-gray-500 text-sm">Erstellen Sie Ihren ersten Barcode oben</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {barcodes.map((barcode) => (
                <div key={barcode.id} className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6">
                  <div className="text-center mb-4">
                    <img
                      src={barcode.barcode_image}
                      alt={`Barcode für ${barcode.text}`}
                      className="mx-auto max-w-full h-auto border border-gray-200 rounded-lg"
                    />
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Text:</p>
                      <p className="text-lg font-mono text-gray-800 break-all">{barcode.text}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-gray-500">Erstellt am:</p>
                      <p className="text-sm text-gray-600">{formatDate(barcode.created_at)}</p>
                    </div>
                    
                    <div className="flex space-x-2 pt-3">
                      <button
                        onClick={() => downloadBarcode(barcode)}
                        className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Download
                      </button>
                      <button
                        onClick={() => deleteBarcode(barcode.id)}
                        className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                        Löschen
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Code128 Barcode Generator - Kostenlos auf Render gehostet 🚀</p>
        </div>
      </div>
    </div>
  );
}

export default App;