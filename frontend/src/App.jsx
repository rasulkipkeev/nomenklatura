import { useState } from 'react';
import { Uploader } from './components/Uploader';
import { MatchingTable } from './components/MatchingTable';
import { Download, LayoutDashboard } from 'lucide-react';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-12">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-blue-500">
              Matcher Про
            </h1>
          </div>

          <div className="flex items-center space-x-3">
            <a
              href="http://localhost:8000/api/export/?format=csv"
              className="flex items-center px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Экспорт в 1С (CSV)
            </a>
            <a
              href="http://localhost:8000/api/export/?format=xml"
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-slate-800 border border-transparent rounded-lg shadow-sm hover:bg-slate-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2 text-slate-300" />
              Экспорт в 1С (XML)
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        <section>
          <Uploader onUploadSuccess={handleUploadSuccess} />
        </section>

        <section>
          <MatchingTable refreshTrigger={refreshTrigger} />
        </section>
      </main>
    </div>
  );
}

export default App;
