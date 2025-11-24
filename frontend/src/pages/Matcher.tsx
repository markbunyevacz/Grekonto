import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Check, X, ArrowLeft, Loader2 } from 'lucide-react';

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
  match_candidate?: any;
}

export default function Matcher() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const taskId = searchParams.get('taskId');
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) {
        navigate('/dashboard');
        return;
    }

    fetch(`/api/tasks`)
        .then(res => res.json())
        .then((data: Task[]) => {
            const found = data.find(t => t.id === taskId);
            if (found) {
                setTask(found);
            } else {
                alert("Feladat nem található!");
                navigate('/dashboard');
            }
            setLoading(false);
        })
        .catch(err => {
            console.error(err);
            setLoading(false);
        });
  }, [taskId, navigate]);

  const handleDecision = async (decision: 'approve' | 'reject') => {
    if (!task) return;
    
    try {
      const newStatus = decision === 'approve' ? 'COMPLETED' : 'REJECTED';
      
      // Send status AND match_candidate if we have one
      const body: any = { status: newStatus };
      if (task.match_candidate) {
          body.match_candidate = task.match_candidate;
      }

      await fetch(`/api/tasks/${task.id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      navigate('/dashboard');
    } catch (error) {
      alert("Hiba történt a mentéskor.");
    }
  };

  if (loading) {
      return (
          <div className="h-screen flex items-center justify-center bg-slate-50">
            <Loader2 className="animate-spin text-slate-400" size={32} />
          </div>
      );
  }

  if (!task) return null;

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto">
        <button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-slate-500 hover:text-slate-700 mb-6 transition-colors"
        >
            <ArrowLeft size={20} /> Vissza a műszerfalra
        </button>

        <div className="bg-white rounded-xl shadow-lg overflow-hidden grid grid-cols-2 h-[600px]">
            {/* Left: Document Preview */}
            <div className="bg-slate-100 p-4 flex items-center justify-center border-r border-slate-200 overflow-auto">
                {task.document_url ? (
                    <img
                        src={task.document_url}
                        alt="Document"
                        className="max-w-full max-h-full object-contain shadow-lg"
                    />
                ) : (
                    <div className="text-slate-400 text-center">
                        <p className="mb-2">Dokumentum előnézet</p>
                        <p className="text-xs">Nincs elérhető kép</p>
                    </div>
                )}
            </div>

            {/* Right: Data & Actions */}
            <div className="p-8 flex flex-col">
                <h1 className="text-2xl font-bold text-slate-900 mb-6">Adatok ellenőrzése</h1>
                
                <div className="space-y-4 flex-1">
                    <div>
                        <label className="block text-xs font-medium text-slate-500 uppercase mb-1">Szállító</label>
                        <div className="text-lg font-medium text-slate-900">{task.extracted.vendor}</div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-medium text-slate-500 uppercase mb-1">Összeg</label>
                            <div className="text-lg font-medium text-slate-900">
                                {task.extracted.amount} {task.extracted.currency}
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-slate-500 uppercase mb-1">Dátum</label>
                            <div className="text-lg font-medium text-slate-900">{task.extracted.date}</div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-8 pt-8 border-t border-slate-100">
                    <button 
                        onClick={() => handleDecision('reject')}
                        className="flex items-center justify-center gap-2 px-4 py-3 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-rose-600 font-medium transition-colors"
                    >
                        <X size={20} /> Elutasítás
                    </button>
                    <button 
                        onClick={() => handleDecision('approve')}
                        className="flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors shadow-indigo-200 shadow-lg"
                    >
                        <Check size={20} /> Jóváhagyás
                    </button>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
