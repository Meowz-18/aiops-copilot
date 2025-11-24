import React from 'react';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';
import type { Incident, Severity } from '../types';

interface IncidentCardProps {
    incident: Incident;
    onClick: (incident: Incident) => void;
}

const severityColors: Record<Severity, string> = {
    low: 'bg-blue-100 text-blue-800 border-blue-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200',
};

export const IncidentCard: React.FC<IncidentCardProps> = ({ incident, onClick }) => {
    return (
        <div
            onClick={() => onClick(incident)}
            className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer flex flex-col gap-3 h-full"
        >
            <div className="flex justify-between items-start">
                <div className={`px-2 py-1 rounded-full text-xs font-medium border ${severityColors[incident.severity]}`}>
                    {incident.severity.toUpperCase()}
                </div>
                <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {new Date(incident.createdAt).toLocaleString()}
                </div>
            </div>

            <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">{incident.service}</h3>
                <p className="text-sm text-gray-600 line-clamp-2">{incident.summary}</p>
            </div>

            <div className="mt-auto flex items-center justify-between pt-2 border-t border-gray-100">
                <span className={`text-xs font-medium flex items-center gap-1 ${incident.status === 'resolved' ? 'text-green-600' : 'text-blue-600'}`}>
                    {incident.status === 'resolved' ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                    {incident.status === 'resolved' ? 'Resolved' : 'Open'}
                </span>
            </div>
        </div>
    );
};
