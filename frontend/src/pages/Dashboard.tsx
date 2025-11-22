import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, XCircle, ArrowRight, Loader2, UploadCloud } from 'lucide-react';
import clsx from 'clsx';
import UploadStatusModal from '../components/UploadStatusModal';

interface Task {
  id: string;
  status: string;
  confidence: number;
  document_url: string;
  extracted: {
    vendor: string;
    amount: number;
    currency: string;
    date: string;
    invoice_id: string;
  };
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'YELLOW' | 'RED'>('ALL');
  const [uploadingFileId, setUploadingFileId] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/tasks')
      .then(res => res.json())
      .then(data => {
        setTasks(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch tasks:", err);
        setLoading(false);
      });
  }, []);

  const filteredTasks = tasks.filter(t => {
    if (filter === 'ALL') return true;
    return t.status === filter;
  });

  const stats = {
    auto: 142, // Mock
    pending: tasks.length
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      try {
        const res = await fetch('/api/upload', {
          method: 'POST',
          headers: {
            'x-filename': file.name
          },
          body: file
        });

        if (res.ok) {
          const data = await res.json();
          // Show status modal
          setUploadingFileId(data.file_id);
        } else {
          const error = await res.json();
          alert(`Hiba a feltöltés során: ${error.error || 'Ismeretlen hiba'}`);
        }
      } catch (err) {
        console.error(err);
        alert("Hiba a feltöltés során.");
      }
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="animate-spin text-slate-400" size={32} />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Mai Statisztika</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center font-bold text-xl">
              {stats.auto}
            </div>
            <div>
              <p className="text-sm text-slate-500">Automatikusan feldolgozva</p>
              <p className="font-medium text-slate-900">Zöld út (AOC)</p>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center font-bold text-xl">
              {stats.pending}
            </div>
            <div>
              <p className="text-sm text-slate-500">Ellenőrzésre vár</p>
              <p className="font-medium text-slate-900">Teendő lista</p>
            </div>
          </div>
          
          {/* Upload Zone */}
          <label className="bg-indigo-50 hover:bg-indigo-100 border-2 border-dashed border-indigo-200 p-4 rounded-lg flex items-center justify-center gap-3 cursor-pointer transition-colors group">
            <UploadCloud className="text-indigo-500 group-hover:scale-110 transition-transform" />
            <div>
              <p className="text-sm font-medium text-indigo-700">Új fájl feltöltése</p>
              <p className="text-xs text-indigo-400">Húzd ide vagy kattints</p>
            </div>
            <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.jpg,.png,.jpeg" />
          </label>
        </div>
      </header>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex justify-between items-center">
          <h2 className="font-bold text-slate-900">Ellenőrzésre váró tételek ({tasks.length})</h2>
          <div className="flex gap-2">
            {(['ALL', 'YELLOW', 'RED'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={clsx(
                  "px-3 py-1 rounded-full text-xs font-medium transition-colors",
                  filter === f 
                    ? "bg-slate-900 text-white" 
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                )}
              >
                {f === 'ALL' ? 'Mind' : f === 'YELLOW' ? 'Csak Sárga' : 'Csak Piros'}
              </button>
            ))}
          </div>
        </div>

        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-6 py-3 font-medium">Státusz</th>
              <th className="px-6 py-3 font-medium">Szállító (AI tipp)</th>
              <th className="px-6 py-3 font-medium">Összeg</th>
              <th className="px-6 py-3 font-medium">Dátum</th>
              <th className="px-6 py-3 font-medium text-right">Akció</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredTasks.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                  Nincs megjeleníthető feladat.
                </td>
              </tr>
            ) : (
              filteredTasks.map((task) => (
                <tr key={task.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    {task.status === 'YELLOW' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 text-amber-700 text-xs font-medium">
                        <AlertTriangle size={12} />
                        {task.confidence}%
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-100 text-rose-700 text-xs font-medium">
                        <XCircle size={12} />
                        Nincs Match
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-900">
                    {task.extracted.vendor || "Ismeretlen"}
                  </td>
                  <td className="px-6 py-4 text-slate-600">
                    {task.extracted.amount ? `${task.extracted.amount.toLocaleString()} ${task.extracted.currency}` : "-"}
                  </td>
                  <td className="px-6 py-4 text-slate-600">
                    {task.extracted.date || "-"}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link 
                      to={`/matcher?taskId=${task.id}`}
                      className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      Nyitás <ArrowRight size={16} />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Upload Status Modal */}
      {uploadingFileId && (
        <UploadStatusModal
          fileId={uploadingFileId}
          onClose={() => setUploadingFileId(null)}
        />
      )}
    </div>
  );
}
