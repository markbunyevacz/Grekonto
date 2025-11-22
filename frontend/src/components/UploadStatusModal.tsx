import { useEffect, useState } from 'react';
import { X, CheckCircle, Loader2, AlertCircle, FileText } from 'lucide-react';

interface ProcessingStage {
  stage: string;
  status: string;
  message: string;
  timestamp: string;
  error?: string;
}

interface ProcessingStatus {
  file_id: string;
  file_name: string;
  overall_status: string;
  current_stage: string;
  current_status: string;
  started_at: string;
  last_updated: string;
  error_message: string;
  stages: ProcessingStage[];
}

interface Props {
  fileId: string | null;
  onClose: () => void;
}

const stageLabels: Record<string, string> = {
  'UPLOAD_STARTED': '📤 Feltöltés indítása',
  'UPLOADED': '✅ Feltöltve',
  'OCR_STARTED': '🤖 OCR feldolgozás indítása',
  'OCR_COMPLETED': '✅ OCR befejezve',
  'OCR_SKIPPED': '⚠️ OCR kihagyva',
  'MATCHING_STARTED': '🔍 Párosítás indítása',
  'MATCHING_COMPLETED': '✅ Párosítás befejezve',
  'COMPLETED': '🎉 Feldolgozás kész',
  'FAILED': '❌ Hiba történt'
};

export default function UploadStatusModal({ fileId, onClose }: Props) {
  const [status, setStatus] = useState<ProcessingStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!fileId) return;

    const fetchStatus = async () => {
      try {
        const res = await fetch(`/api/status/${fileId}`);
        if (res.ok) {
          const data = await res.json();
          // Validate and set status with defaults for missing fields
          setStatus({
            ...data,
            stages: data.stages || [],
            file_name: data.file_name || data.file_id || 'Fájl',
            overall_status: data.overall_status || 'IN_PROGRESS',
            current_stage: data.current_stage || '',
            current_status: data.current_status || '',
            error_message: data.error_message || ''
          });
          
          // Auto-close if completed or failed
          if (data.overall_status === 'COMPLETED' || data.overall_status === 'FAILED') {
            setTimeout(() => {
              onClose();
              window.location.reload(); // Refresh to show new task
            }, 3000);
          }
        } else {
          setError('Státusz nem található');
        }
      } catch (err) {
        setError('Hiba a státusz lekérdezése során');
        console.error(err);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 2 seconds
    const interval = setInterval(fetchStatus, 2000);

    return () => clearInterval(interval);
  }, [fileId, onClose]);

  if (!fileId) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Feldolgozás Állapota</h2>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-600"
            aria-label="Bezárás"
          >
            <X size={24} />
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {status && (
          <div className="space-y-6">
            {/* Overall Status */}
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex items-center gap-3">
                {status.overall_status === 'IN_PROGRESS' && (
                  <Loader2 className="animate-spin text-blue-500" size={24} />
                )}
                {status.overall_status === 'COMPLETED' && (
                  <CheckCircle className="text-green-500" size={24} />
                )}
                {status.overall_status === 'FAILED' && (
                  <AlertCircle className="text-red-500" size={24} />
                )}
                <div>
                  <p className="font-semibold text-slate-900">
                    {status.overall_status === 'IN_PROGRESS' && 'Feldolgozás folyamatban...'}
                    {status.overall_status === 'COMPLETED' && 'Feldolgozás sikeres!'}
                    {status.overall_status === 'FAILED' && 'Feldolgozás sikertelen'}
                  </p>
                  <p className="text-sm text-slate-500">{status.file_name || status.file_id || 'Fájl'}</p>
                </div>
              </div>
            </div>

            {/* Processing Stages */}
            {status.stages && status.stages.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-slate-700">Feldolgozási lépések:</h3>
                {status.stages.map((stage, index) => (
                  <div
                    key={index}
                    className={`border-l-4 pl-4 py-2 ${
                      stage.status === 'SUCCESS'
                        ? 'border-green-500 bg-green-50'
                        : stage.status === 'ERROR'
                        ? 'border-red-500 bg-red-50'
                        : 'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-slate-900">
                          {stageLabels[stage.stage] || stage.stage}
                        </p>
                        <p className="text-sm text-slate-600 mt-1">{stage.message}</p>
                        {stage.error && (
                          <p className="text-sm text-red-600 mt-1 font-mono bg-red-100 p-2 rounded">
                            {stage.error}
                          </p>
                        )}
                      </div>
                      {stage.timestamp && (
                        <span className="text-xs text-slate-400 ml-4">
                          {new Date(stage.timestamp).toLocaleTimeString('hu-HU')}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Error Message */}
            {status.error_message && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="font-semibold text-red-800 mb-2">Hiba részletei:</p>
                <p className="text-sm text-red-700 font-mono">{status.error_message}</p>
              </div>
            )}
          </div>
        )}

        {!status && !error && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-slate-400" size={32} />
          </div>
        )}
      </div>
    </div>
  );
}

