import React from 'react';
import type { Incident } from '../types';
import { IncidentCard } from './IncidentCard';
import { Loader2, Search } from 'lucide-react';

interface IncidentListProps {
    incidents: Incident[];
    isLoading: boolean;
    onIncidentClick: (incident: Incident) => void;
    filterStatus: string;
    setFilterStatus: (status: string) => void;
    filterSeverity: string;
    setFilterSeverity: (severity: string) => void;
    searchTerm: string;
    setSearchTerm: (term: string) => void;
}

export const IncidentList: React.FC<IncidentListProps> = ({
    incidents,
    isLoading,
    onIncidentClick,
    filterStatus,
    setFilterStatus,
    filterSeverity,
    setFilterSeverity,
    searchTerm,
    setSearchTerm,
}) => {
    const filteredIncidents = incidents.filter(incident => {
        const matchesStatus = filterStatus === 'all' || incident.status === filterStatus;
        const matchesSeverity = filterSeverity === 'all' || incident.severity === filterSeverity;
        const matchesSearch =
            incident.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
            incident.service.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesStatus && matchesSeverity && matchesSearch;
    });

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900">Incidents</h2>

                <div className="flex flex-wrap gap-3 items-center w-full sm:w-auto">
                    <div className="relative flex-1 sm:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search incidents..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>

                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white"
                    >
                        <option value="all">All Status</option>
                        <option value="open">Open</option>
                        <option value="resolved">Resolved</option>
                    </select>

                    <select
                        value={filterSeverity}
                        onChange={(e) => setFilterSeverity(e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white"
                    >
                        <option value="all">All Severities</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>
            </div>

            {isLoading ? (
                <div className="flex justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
            ) : filteredIncidents.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                    <p className="text-gray-500">No incidents found matching your filters.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredIncidents.map(incident => (
                        <IncidentCard
                            key={incident.incidentId}
                            incident={incident}
                            onClick={onIncidentClick}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};
