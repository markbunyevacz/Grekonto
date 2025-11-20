import { Search, CheckCircle, AlertTriangle, Trash2, Clock } from 'lucide-react';
import { useEffect, useState } from 'react';

interface LogEntry {
  time: string;
  file: string;
  client: string;
  result: string;
  user: string;
  message: string;
}

export default function History() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/get_history')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setLogs(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch history", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Feldolgozási Napló</h1>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Keresés fájlnévre..." 
            className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 w-64"
          />
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-6 py-3 font-medium">Időpont</th>
              <th className="px-6 py-3 font-medium">Fájlnév</th>
              <th className="px-6 py-3 font-medium">Ügyfél</th>
              <th className="px-6 py-3 font-medium">Eredmény</th>
              <th className="px-6 py-3 font-medium">Felhasználó</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-slate-500">Betöltés...</td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-slate-500">Nincs megjeleníthető adat.</td>
              </tr>
            ) : (
              logs.map((log, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="px-6 py-4 text-slate-600">{log.time}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{log.file}</td>
                  <td className="px-6 py-4 text-slate-600">{log.client}</td>
                  <td className="px-6 py-4">
                    {log.result === 'MATCH' && (
                      <span className="inline-flex items-center gap-1 text-emerald-600 text-xs font-medium">
                        <CheckCircle size={12} /> Párosítva
                      </span>
                    )}
                    {(log.result === 'MANUAL' || log.result === 'MANUAL_REVIEW_REQUIRED') && (
                      <span className="inline-flex items-center gap-1 text-amber-600 text-xs font-medium">
                        <AlertTriangle size={12} /> Kézi
                      </span>
                    )}
                    {log.result === 'PROCESSING_STARTED' && (
                      <span className="inline-flex items-center gap-1 text-blue-600 text-xs font-medium">
                        <Clock size={12} /> Feldolgozás
                      </span>
                    )}
                    {log.result === 'TRASH' && (
                      <span className="inline-flex items-center gap-1 text-rose-600 text-xs font-medium">
                        <Trash2 size={12} /> Elvetve
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-slate-500 text-xs">{log.user}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
