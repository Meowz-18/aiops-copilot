import React from 'react';
import { X, AlertTriangle, BookOpen, CheckCircle, RotateCcw } from 'lucide-react';
import type { Incident } from '../types';

interface IncidentDrawerProps {
    incident: Incident | null;
    isOpen: boolean;
    onClose: () => void;
    onResolve: (id: string) => void;
    onReopen: (id: string) => void;
}

export const IncidentDrawer: React.FC<IncidentDrawerProps> = ({ incident, isOpen, onClose, onResolve, onReopen }) => {
    if (!isOpen || !incident) return null;

    return (
        <div className="fixed inset-0 z-50 flex justify-end">
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" onClick={onClose} />
            <div className="relative w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
                <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gray-50">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">{incident.service} Incident</h2>
                        <p className="text-sm text-gray-500">ID: {incident.incidentId}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full text-gray-500">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {/* Summary Section */}
                    <section>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Summary</h3>
                        <div className="bg-blue-50 p-4 rounded-lg text-blue-900 border border-blue-100">
                            {incident.summary}
                        </div>
                    </section>

                    {/* Root Cause Section */}
                    <section>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            Root Cause Analysis
                        </h3>
                        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                            <p className="text-gray-800 leading-relaxed">{incident.rootCause}</p>
                        </div>
                    </section>

                    {/* Runbook Section */}
                    <section>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <BookOpen className="w-4 h-4" />
                            Recommended Runbook
                        </h3>
                        <div className="bg-gray-900 text-gray-100 p-5 rounded-lg font-mono text-sm overflow-x-auto">
                            <pre className="whitespace-pre-wrap">{incident.runbookSteps}</pre>
                        </div>
                    </section>
                </div>

                <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
                    {incident.status === 'open' ? (
                        <button
                            onClick={() => onResolve(incident.incidentId)}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                        >
                            <CheckCircle className="w-4 h-4" />
                            Mark as Resolved
                        </button>
                    ) : (
                        <button
                            onClick={() => onReopen(incident.incidentId)}
                            className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Reopen Incident
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};
