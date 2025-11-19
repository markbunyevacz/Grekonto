import { useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = () => {
    // Mock login
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-md rounded-xl shadow-lg p-8 text-center">
        <div className="w-16 h-16 bg-indigo-600 rounded-2xl mx-auto flex items-center justify-center mb-6 shadow-indigo-200 shadow-lg">
          <span className="text-white text-3xl font-bold">G</span>
        </div>
        
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Üdvözlünk az AI Rendszerben</h1>
        <p className="text-slate-500 mb-8">Jelentkezz be a folytatáshoz</p>

        <button 
          onClick={handleLogin}
          className="w-full bg-[#2F2F2F] hover:bg-[#1a1a1a] text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-3 transition-colors mb-6"
        >
          <div className="w-5 h-5 bg-white rounded-sm flex items-center justify-center">
             {/* Microsoft Logo Mock */}
             <div className="grid grid-cols-2 gap-[1px]">
                <div className="w-2 h-2 bg-[#F25022]"></div>
                <div className="w-2 h-2 bg-[#7FBA00]"></div>
                <div className="w-2 h-2 bg-[#00A4EF]"></div>
                <div className="w-2 h-2 bg-[#FFB900]"></div>
             </div>
          </div>
          Bejelentkezés Microsoft fiókkal
        </button>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-slate-500">vagy e-mail címmel</span>
          </div>
        </div>

        <form className="space-y-4 text-left" onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">E-mail cím</label>
            <input 
              type="email" 
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
              placeholder="pelda@grekonto.hu"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Jelszó</label>
            <input 
              type="password" 
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
              placeholder="••••••••"
            />
          </div>
          <button 
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            Belépés
          </button>
        </form>

        <div className="mt-8 text-xs text-slate-400 flex items-center justify-center gap-1">
          <ShieldCheck size={12} />
          <span>Biztonságos kapcsolat | © 2025 Grekonto</span>
        </div>
      </div>
    </div>
  );
}
