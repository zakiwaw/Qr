import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'https://qr-3ju2.onrender.com';

const MODE_CONFIG = {
  barcode: {
    highlight: 'Code128',
    title: 'Barcode Generator',
    subtitle: 'Erstellen Sie Code128 Barcodes aus Text und Zahlen',
    listEndpoint: '/api/barcodes',
    listKey: 'barcodes',
    generateEndpoint: '/api/generate-barcode',
    deleteEndpoint: '/api/barcode',
    generatingLabel: 'Generiere Barcode...',
    buttonLabel: 'Barcode Generieren',
    loadingLabel: 'Lade Barcodes...',
    emptyTitle: 'Noch keine Barcodes generiert',
    emptySubtitle: 'Erstellen Sie Ihren ersten Barcode oben',
    listTitle: 'Generierte Barcodes',
    errorLoad: 'Fehler beim Laden der Barcodes',
    errorGenerate: 'Fehler beim Generieren des Barcodes',
    errorDelete: 'Fehler beim Löschen des Barcodes',
    downloadPrefix: 'barcode',
    imageKey: 'barcode_image',
    altLabel: 'Barcode',
    emptyIcon: '📊',
    inputLabel: 'Text oder Nummern eingeben',
    placeholder: 'z.B. Hello World oder 123456789',
  },
  qrcode: {
    highlight: 'QR-Code',
    title: 'Generator',
    subtitle: 'Erstellen Sie QR-Codes für Links, Texte und mehr',
    listEndpoint: '/api/qrcodes',
    listKey: 'qrcodes',
    generateEndpoint: '/api/generate-qrcode',
    deleteEndpoint: '/api/qrcode',
    generatingLabel: 'Generiere QR-Code...',
    buttonLabel: 'QR-Code Generieren',
    loadingLabel: 'Lade QR-Codes...',
    emptyTitle: 'Noch keine QR-Codes generiert',
    emptySubtitle: 'Erstellen Sie Ihren ersten QR-Code oben',
    listTitle: 'Generierte QR-Codes',
    errorLoad: 'Fehler beim Laden der QR-Codes',
    errorGenerate: 'Fehler beim Generieren des QR-Codes',
    errorDelete: 'Fehler beim Löschen des QR-Codes',
    downloadPrefix: 'qrcode',
    imageKey: 'qrcode_image',
    altLabel: 'QR-Code',
    emptyIcon: '🔳',
    inputLabel: 'Text, URL oder Nummern eingeben',
    placeholder: 'z.B. https://example.com oder Kontaktinformationen',
  },
};

function App() {
  const [inputText, setInputText] = useState('');
  const [mode, setMode] = useState('barcode');
  const [codes, setCodes] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCodes = useCallback(async () => {
    const { listEndpoint, listKey, errorLoad } = MODE_CONFIG[mode];
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}${listEndpoint}`);
      setCodes(response.data[listKey] ?? []);
      setError('');
    } catch (err) {
      setError(errorLoad);
      console.error('Error fetching codes:', err);
    } finally {
      setIsLoading(false);
    }
  }, [mode]);

  useEffect(() => {
    fetchCodes();
  }, [fetchCodes]);

  const handleModeChange = (newMode) => {
    if (newMode === mode) {
      return;
    }
    setMode(newMode);
    setInputText('');
    setError('');
    setCodes([]);
    setIsLoading(true);
  };

  const generateCode = async (e) => {
    e.preventDefault();

    if (!inputText.trim()) {
      setError('Bitte geben Sie Text oder Zahlen ein');
      return;
    }

    const { generateEndpoint, errorGenerate } = MODE_CONFIG[mode];

    try {
      setIsGenerating(true);
      setError('');

      const response = await axios.post(`${API_BASE_URL}${generateEndpoint}`, {
        text: inputText.trim(),
      });

      setCodes((prev) => [response.data, ...prev]);
      setInputText('');
    } catch (err) {
      setError(err.response?.data?.detail || errorGenerate);
      console.error('Error generating code:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const deleteCode = async (codeId) => {
    const { deleteEndpoint, errorDelete } = MODE_CONFIG[mode];
    try {
      await axios.delete(`${API_BASE_URL}${deleteEndpoint}/${codeId}`);
      setCodes((prev) => prev.filter((code) => code.id !== codeId));
    } catch (err) {
      setError(errorDelete);
      console.error('Error deleting code:', err);
    }
  };

  const downloadCode = (code) => {
    const { imageKey, downloadPrefix } = MODE_CONFIG[mode];
    const link = document.createElement('a');
    link.href = code[imageKey];
    link.download = `${downloadPrefix}-${code.text}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('de-DE');
  };

  const config = MODE_CONFIG[mode];
  const imageKey = config.imageKey;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            <span className="text-indigo-600">{config.highlight}</span> {config.title}
          </h1>
          <p className="text-gray-600">{config.subtitle}</p>
        </div>

        {/* Mode Switcher */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-full shadow-md p-1 flex">
            {[
              { key: 'barcode', label: 'Barcode' },
              { key: 'qrcode', label: 'QR-Code' },
            ].map((option) => (
              <button
                key={option.key}
                type="button"
                onClick={() => handleModeChange(option.key)}
                className={`px-4 py-2 rounded-full font-medium transition-colors ${
                  mode === option.key
                    ? 'bg-indigo-600 text-white shadow'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
                aria-pressed={mode === option.key}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Generator Form */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <form onSubmit={generateCode} className="space-y-4">
              <div>
                <label htmlFor="inputText" className="block text-sm font-medium text-gray-700 mb-2">
                  {config.inputLabel}
                </label>
                <input
                  type="text"
                  id="inputText"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={config.placeholder}
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
                    {config.generatingLabel}
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    {config.buttonLabel}
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Codes List */}
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">{config.listTitle}</h2>
            <button
              onClick={fetchCodes}
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
              <p className="mt-4 text-gray-600">{config.loadingLabel}</p>
            </div>
          ) : codes.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">{config.emptyIcon}</div>
              <p className="text-gray-600">{config.emptyTitle}</p>
              <p className="text-gray-500 text-sm">{config.emptySubtitle}</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {codes.map((code) => (
                <div key={code.id} className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6">
                  <div className="text-center mb-4">
                    <img
                      src={code[imageKey]}
                      alt={`${config.altLabel} für ${code.text}`}
                      className="mx-auto max-w-full h-auto border border-gray-200 rounded-lg"
                    />
                  </div>

                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Text:</p>
                      <p className="text-lg font-mono text-gray-800 break-all">{code.text}</p>
                    </div>

                    <div>
                      <p className="text-sm font-medium text-gray-500">Erstellt am:</p>
                      <p className="text-sm text-gray-600">{formatDate(code.created_at)}</p>
                    </div>

                    <div className="flex space-x-2 pt-3">
                      <button
                        onClick={() => downloadCode(code)}
                        className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Download
                      </button>
                      <button
                        onClick={() => deleteCode(code.id)}
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
      </div>
    </div>
  );
}

export default App;
