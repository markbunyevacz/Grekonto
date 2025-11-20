import { useState, useEffect } from 'react';
import { Plus, Trash2, CheckCircle, Loader2 } from 'lucide-react';

export default function Settings() {
  const [showModal, setShowModal] = useState(false);
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    partner: '',
    server: 'imap.gmail.com',
    port: '993',
    user: '',
    password: ''
  });

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const res = await fetch('/api/settings/sources');
      if (res.ok) {
        const data = await res.json();
        setSources(data);
      }
    } catch (error) {
      console.error("Failed to fetch sources", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.partner || !formData.server || !formData.user || !formData.password) {
      alert("Minden mező kitöltése kötelező!");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch('/api/settings/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        setShowModal(false);
        setFormData({
          partner: '',
          server: 'imap.gmail.com',
          port: '993',
          user: '',
          password: ''
        });
        fetchSources();
      } else {
        alert("Hiba történt a mentéskor.");
      }
    } catch (error) {
      console.error("Save failed", error);
      alert("Hiba történt a mentéskor.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="h-full flex items-center justify-center"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Adatforrások Kezelése</h1>
          <p className="text-slate-500">Itt állíthatod be, honnan gyűjtse az AI a számlákat.</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors"
        >
          <Plus size={18} />
          Új forrás
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-6 py-3 font-medium">Típus</th>
              <th className="px-6 py-3 font-medium">Név / Cím</th>
              <th className="px-6 py-3 font-medium">Ügyfél</th>
              <th className="px-6 py-3 font-medium">Állapot</th>
              <th className="px-6 py-3 font-medium text-right">Művelet</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sources.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                  Nincs beállított adatforrás.
                </td>
              </tr>
            )}
            {sources.map((source, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-slate-100 rounded text-xs font-medium text-slate-600">
                    IMAP
                  </span>
                </td>
                <td className="px-6 py-4 font-medium text-slate-900">{source.user}</td>
                <td className="px-6 py-4 text-slate-600">{source.partner}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1 text-emerald-600 text-xs font-medium">
                    <CheckCircle size={12} /> OK
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-slate-400 hover:text-rose-600 transition-colors">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-slate-900">Új E-mail Fiók Bekötése</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <Plus size={24} className="rotate-45" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Melyik ügyfélhez tartozik?</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Pl. Kovács Bt."
                  value={formData.partner}
                  onChange={e => setFormData({...formData, partner: e.target.value})}
                />
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Szerver címe</label>
                  <input 
                    type="text" 
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg" 
                    value={formData.server}
                    onChange={e => setFormData({...formData, server: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Port</label>
                  <input 
                    type="text" 
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg" 
                    value={formData.port}
                    onChange={e => setFormData({...formData, port: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Felhasználó</label>
                <input 
                  type="email" 
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg" 
                  placeholder="user@example.com" 
                  value={formData.user}
                  onChange={e => setFormData({...formData, user: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Jelszó</label>
                <input 
                  type="password" 
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg" 
                  placeholder="App Password" 
                  value={formData.password}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                />
              </div>

              <div className="pt-4 flex gap-3">
                <button className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-2 rounded-lg">
                  Teszt Kapcsolódás
                </button>
                <button 
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg disabled:opacity-50"
                >
                  {saving ? 'Mentés...' : 'Mentés'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}