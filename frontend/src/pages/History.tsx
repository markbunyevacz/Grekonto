import { Search, CheckCircle, AlertTriangle, Trash2 } from 'lucide-react';

export default function History() {
  const logs = [
    { time: 'Ma 10:05', file: 'INV_882.pdf', client: 'MVM Next', result: 'MATCH', user: 'Orbita' },
    { time: 'Ma 09:45', file: 'scan002.jpg', client: 'Praktiker', result: 'MANUAL', user: 'AI' },
    { time: 'Ma 08:00', file: 'menu.pdf', client: '-', result: 'TRASH', user: 'Orbita' },
  ];

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
            {logs.map((log, idx) => (
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
                  {log.result === 'MANUAL' && (
                    <span className="inline-flex items-center gap-1 text-amber-600 text-xs font-medium">
                      <AlertTriangle size={12} /> Kézi
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
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
