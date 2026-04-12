import { useState, useRef } from 'react';
import { treasurerAPI } from '../services/api';

interface ParsedMember {
  name: string;
  email: string;
}

interface ImportResult {
  created: { name: string; email: string }[];
  skipped: { name: string; email: string; reason: string }[];
  errors: { name: string; email: string; reason: string }[];
}

interface Props {
  onClose: () => void;
  onImported: () => void;
}

function parseCSV(text: string): ParsedMember[] {
  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  if (lines.length === 0) return [];

  // Detect if first line is a header (contains "name" or "email")
  const firstLower = lines[0].toLowerCase();
  const hasHeader = firstLower.includes('name') || firstLower.includes('email');
  const dataLines = hasHeader ? lines.slice(1) : lines;

  return dataLines
    .map((line) => {
      // Handle quoted fields
      const cols = line.split(',').map((c) => c.replace(/^"|"$/g, '').trim());
      const name = cols[0] || '';
      const email = cols[1] || '';
      return { name, email };
    })
    .filter((m) => m.name || m.email);
}

function BulkImportModal({ onClose, onImported }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<ParsedMember[] | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (file: File) => {
    setParseError(null);
    setPreview(null);
    setResult(null);

    if (!file.name.endsWith('.csv') && file.type !== 'text/csv' && file.type !== 'text/plain') {
      setParseError('Please upload a CSV file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const parsed = parseCSV(text);
      if (parsed.length === 0) {
        setParseError('No valid rows found. Make sure the CSV has name and email columns.');
        return;
      }
      setPreview(parsed);
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleImport = async () => {
    if (!preview || preview.length === 0) return;
    setIsImporting(true);
    try {
      const res = await treasurerAPI.bulkImportMembers(preview);
      setResult(res);
      if (res.created.length > 0) {
        onImported();
      }
    } catch (err: any) {
      setParseError(err.response?.data?.error || 'Import failed. Please try again.');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative glass-card w-full max-w-2xl max-h-[90vh] flex flex-col animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-surface-border">
          <div>
            <h2 className="font-heading text-xl font-semibold text-white">Import Members</h2>
            <p className="text-sm text-gray-400 mt-0.5">
              Upload a CSV with <code className="text-royal-400">name</code> and{' '}
              <code className="text-royal-400">email</code> columns. Each new member will receive
              a setup email.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-surface-hover transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Result state */}
          {result ? (
            <div className="space-y-4">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-4 text-center">
                  <div className="text-2xl font-heading font-bold text-emerald-400">{result.created.length}</div>
                  <div className="text-xs text-emerald-300 mt-1">Imported</div>
                </div>
                <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-4 text-center">
                  <div className="text-2xl font-heading font-bold text-amber-400">{result.skipped.length}</div>
                  <div className="text-xs text-amber-300 mt-1">Skipped</div>
                </div>
                <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-center">
                  <div className="text-2xl font-heading font-bold text-rose-400">{result.errors.length}</div>
                  <div className="text-xs text-rose-300 mt-1">Errors</div>
                </div>
              </div>

              {result.created.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-emerald-400 mb-2">
                    Successfully imported — setup emails sent
                  </p>
                  <div className="rounded-lg border border-surface-border overflow-hidden">
                    <table className="min-w-full text-sm">
                      <tbody>
                        {result.created.map((m, i) => (
                          <tr key={i} className="border-t border-surface-border first:border-0">
                            <td className="px-4 py-2.5 text-white">{m.name}</td>
                            <td className="px-4 py-2.5 text-gray-400">{m.email}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {result.skipped.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-amber-400 mb-2">Skipped (already exist)</p>
                  <div className="rounded-lg border border-surface-border overflow-hidden">
                    <table className="min-w-full text-sm">
                      <tbody>
                        {result.skipped.map((m, i) => (
                          <tr key={i} className="border-t border-surface-border first:border-0">
                            <td className="px-4 py-2.5 text-white">{m.name}</td>
                            <td className="px-4 py-2.5 text-gray-400">{m.email}</td>
                            <td className="px-4 py-2.5 text-amber-400 text-xs">{m.reason}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {result.errors.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-rose-400 mb-2">Errors</p>
                  <div className="rounded-lg border border-surface-border overflow-hidden">
                    <table className="min-w-full text-sm">
                      <tbody>
                        {result.errors.map((m, i) => (
                          <tr key={i} className="border-t border-surface-border first:border-0">
                            <td className="px-4 py-2.5 text-white">{m.name || '—'}</td>
                            <td className="px-4 py-2.5 text-gray-400">{m.email || '—'}</td>
                            <td className="px-4 py-2.5 text-rose-400 text-xs">{m.reason}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ) : preview ? (
            /* Preview state */
            <div className="space-y-4">
              <p className="text-sm text-gray-400">
                {preview.length} member{preview.length !== 1 ? 's' : ''} ready to import.
                Existing accounts will be skipped automatically.
              </p>
              <div className="rounded-lg border border-surface-border overflow-hidden max-h-64 overflow-y-auto">
                <table className="min-w-full text-sm">
                  <thead className="table-header">
                    <tr>
                      <th className="px-4 py-3 text-left">#</th>
                      <th className="px-4 py-3 text-left">Name</th>
                      <th className="px-4 py-3 text-left">Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((m, i) => (
                      <tr key={i} className="table-row">
                        <td className="table-cell text-gray-500">{i + 1}</td>
                        <td className="table-cell text-white">{m.name || <span className="text-rose-400 italic">missing</span>}</td>
                        <td className="table-cell text-gray-300">{m.email || <span className="text-rose-400 italic">missing</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {parseError && <div className="alert-error">{parseError}</div>}
            </div>
          ) : (
            /* Upload state */
            <div>
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
                  dragOver
                    ? 'border-royal-400 bg-royal-500/10'
                    : 'border-surface-border hover:border-royal-500/50 hover:bg-surface-hover'
                }`}
              >
                <svg className="w-10 h-10 mx-auto mb-3 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-gray-300 font-medium">Drop your CSV here or click to browse</p>
                <p className="text-gray-500 text-sm mt-1">CSV with name, email columns</p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,text/csv,text/plain"
                onChange={handleFileInput}
                className="hidden"
              />

              {parseError && <div className="alert-error mt-4">{parseError}</div>}

              <div className="mt-4 p-3 rounded-lg bg-surface-hover border border-surface-border">
                <p className="text-xs text-gray-500 font-medium mb-1">Expected format:</p>
                <code className="text-xs text-gray-400">
                  name,email<br />
                  John Doe,john@example.com<br />
                  Jane Smith,jane@example.com
                </code>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-surface-border flex items-center justify-end gap-3">
          {result ? (
            <button onClick={onClose} className="btn-primary">Done</button>
          ) : preview ? (
            <>
              <button
                onClick={() => { setPreview(null); setParseError(null); }}
                className="btn-secondary"
                disabled={isImporting}
              >
                Back
              </button>
              <button
                onClick={handleImport}
                disabled={isImporting}
                className={`btn-primary ${isImporting ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {isImporting ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Importing...
                  </span>
                ) : (
                  `Import ${preview.length} Member${preview.length !== 1 ? 's' : ''}`
                )}
              </button>
            </>
          ) : (
            <button onClick={onClose} className="btn-secondary">Cancel</button>
          )}
        </div>
      </div>
    </div>
  );
}

export default BulkImportModal;
