import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ZoomIn, RotateCw, Check, Search, Trash2, X, Loader2 } from 'lucide-react';
import clsx from 'clsx';

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
  match_candidate?: {
    id: number;
    vendor: string;
    amount: number;
    currency: string;
    date: string;
    reason?: string;
  };
}

export default function Matcher() {
  const [searchParams] = useSearchParams();
  const taskId = searchParams.get('taskId');
  const navigate = useNavigate();
  
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [showManualSearch, setShowManualSearch] = useState(false);
  const [manualSearchQuery, setManualSearchQuery] = useState('');

  useEffect(() => {
    if (!taskId) return;

    fetch('/api/tasks')
      .then(res => res.json())
      .then((data: Task[]) => {
        const found = data.find(t => t.id === taskId);
        setTask(found || null);
        setLoading(false);
        if (found?.extracted?.vendor) {
            setManualSearchQuery(found.extracted.vendor);
        }
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [taskId]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (showManualSearch) {
        if (e.key === 'Escape') setShowManualSearch(false);
        return;
      }

      if (e.key === 'Escape') {
        // Maybe go back? Or just nothing.
        // navigate('/dashboard'); 
      }
      // Only allow shortcuts if we have a task and not searching
      if (task) {
        if (e.key === 'Enter') {
           handleDecision('approve');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [task, showManualSearch]);

  const handleDecision = async (decision: 'approve' | 'reject') => {
    if (!task) return;
    
    try {
      const newStatus = decision === 'approve' ? 'COMPLETED' : 'REJECTED';
      await fetch(`/api/tasks/${task.id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      navigate('/dashboard');
    } catch (error) {
      alert("Hiba történt a mentéskor.");
    }
  };

  if (loading) return <div className="h-full flex items-center justify-center"><Loader2 className="animate-spin" /></div>;
  if (!task) return <div className="p-8">Feladat nem található. <Link to="/dashboard" className="text-indigo-600">Vissza</Link></div>;

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex justify-between items-center shrink-0">
        <Link to="/dashboard" className="flex items-center gap-2 text-slate-600 hover:text-slate-900 font-medium">
          <ArrowLeft size={18} /> Vissza a listához
        </Link>
        <h1 className="font-bold text-slate-900">Párosítás Jóváhagyása</h1>
        <div className="w-24"></div> {/* Spacer */}
      </header>

      {/* Main Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Document Viewer */}
        <div className="w-1/2 bg-slate-100 border-r border-slate-200 relative flex flex-col">
          <div className="flex-1 overflow-auto flex items-center justify-center p-8">
            <img 
              src={task.document_url} 
              alt="Document" 
              className="max-w-full shadow-lg"
            />
          </div>
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur shadow-lg rounded-full px-4 py-2 flex gap-4">
            <button className="text-slate-600 hover:text-indigo-600"><ZoomIn size={20} /></button>
            <button className="text-slate-600 hover:text-indigo-600"><RotateCw size={20} /></button>
          </div>
        </div>

        {/* Right: Data & Actions */}
        <div className="w-1/2 bg-white flex flex-col">
          <div className="flex-1 overflow-auto p-8 space-y-8">
            
            {/* 1. Extracted Data */}
            <section>
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">1. AI által felismert adatok</h2>
              <div className="bg-slate-50 rounded-xl p-6 border border-slate-100 space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-500">Szállító:</span>
                  <span className="font-bold text-slate-900">{task.extracted.vendor || "-"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Dátum:</span>
                  <span className="font-medium text-slate-900">{task.extracted.date || "-"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Sorszám:</span>
                  <span className="font-medium text-slate-900">{task.extracted.invoice_id || "-"}</span>
                </div>
                <div className="border-t border-slate-200 pt-3 flex justify-between items-center">
                  <span className="text-slate-500">Végösszeg:</span>
                  <span className="text-xl font-bold text-indigo-600">
                    {task.extracted.amount?.toLocaleString()} {task.extracted.currency}
                  </span>
                </div>
              </div>
            </section>

            {/* 2. Match Candidate */}
            <section>
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">2. NAV (AOC) Találat</h2>
              
              {task.match_candidate ? (
                <div className={clsx(
                  "rounded-xl p-6 border-2 cursor-pointer transition-all relative",
                  task.status === 'YELLOW' ? "border-amber-200 bg-amber-50" : "border-emerald-200 bg-emerald-50"
                )}>
                  <div className="absolute top-4 right-4">
                    <div className={clsx(
                      "w-6 h-6 rounded-full flex items-center justify-center text-white",
                      "bg-indigo-600" // Selected state
                    )}>
                      <Check size={14} />
                    </div>
                  </div>

                  <div className="mb-2">
                    <span className={clsx(
                      "text-xs font-bold px-2 py-1 rounded-full",
                      task.status === 'YELLOW' ? "bg-amber-200 text-amber-800" : "bg-emerald-200 text-emerald-800"
                    )}>
                      {task.status === 'YELLOW' ? 'BIZONYTALAN EGYEZÉS' : 'TÖKÉLETES EGYEZÉS'}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <p className="font-bold text-slate-900">{task.match_candidate.vendor}</p>
                    <p className="text-sm text-slate-600">Dátum: {task.match_candidate.date}</p>
                    <p className="text-sm text-slate-600">Összeg: {task.match_candidate.amount} {task.match_candidate.currency}</p>
                    {task.match_candidate.reason && (
                      <p className="text-xs text-amber-700 mt-2">⚠️ {task.match_candidate.reason}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center p-8 border-2 border-dashed border-slate-200 rounded-xl">
                  <p className="text-slate-500 mb-4">A rendszer nem talált automatikus egyezést.</p>
                  <button 
                    onClick={() => setShowManualSearch(true)}
                    className="text-indigo-600 font-medium hover:underline"
                  >
                    Kézi keresés indítása
                  </button>
                </div>
              )}
            </section>
          </div>

          {/* Action Bar */}
          <div className="p-6 border-t border-slate-200 bg-slate-50 flex gap-4">
            <button 
              onClick={() => handleDecision('reject')}
              className="flex-1 bg-white border border-slate-300 hover:bg-rose-50 hover:border-rose-200 hover:text-rose-700 text-slate-700 font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-colors"
            >
              <Trash2 size={20} />
              ELVETÉS
            </button>
            
            <button 
              onClick={() => setShowManualSearch(true)}
              className="flex-1 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-colors"
            >
              <Search size={20} />
              KÉZI KERESÉS
            </button>

            <button 
              onClick={() => handleDecision('approve')}
              className="flex-[2] bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 transition-colors"
            >
              <CheckCircle size={20} />
              JÓVÁHAGYÁS & BEKÜLDÉS
            </button>
          </div>
        </div>
      </div>

      {/* Manual Search Modal */}
      {showManualSearch && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl flex flex-col max-h-[80vh]">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-900">Kézi Párosítás Keresése</h2>
              <button onClick={() => setShowManualSearch(false)} className="text-slate-400 hover:text-slate-600">
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 bg-slate-50 border-b border-slate-100">
              <div className="flex gap-2">
                <input 
                  type="text" 
                  value={manualSearchQuery}
                  onChange={(e) => setManualSearchQuery(e.target.value)}
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Szállító neve vagy összeg..."
                />
                <button className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium">
                  Keresés
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-auto p-6">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Találatok</p>
              <div className="space-y-2">
                {/* Mock Results */}
                {[1, 2].map((i) => (
                  <div key={i} className="flex items-center p-4 bg-white border border-slate-200 rounded-lg hover:border-indigo-500 cursor-pointer group">
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="font-bold text-slate-900">MVM Next Zrt.</span>
                        <span className="font-medium text-slate-900">14.200 Ft</span>
                      </div>
                      <div className="flex justify-between text-sm text-slate-500">
                        <span>2024.11.15</span>
                        <span>Sorszám: ...888</span>
                      </div>
                    </div>
                    <button className="ml-4 opacity-0 group-hover:opacity-100 bg-indigo-50 text-indigo-600 px-3 py-1 rounded text-sm font-medium">
                      Kiválaszt
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 border-t border-slate-100 bg-slate-50 text-right">
              <button 
                onClick={() => setShowManualSearch(false)}
                className="text-slate-500 hover:text-slate-700 font-medium"
              >
                Mégse
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
