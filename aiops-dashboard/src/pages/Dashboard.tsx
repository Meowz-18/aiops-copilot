import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { LogUploader } from '../components/LogUploader';
import { IncidentList } from '../components/IncidentList';
import { IncidentDrawer } from '../components/IncidentDrawer';
import type { Incident } from '../types';
import { uploadLog, analyzeLogs, fetchIncidents } from '../services/api';

interface DashboardProps {
    onLogout?: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [isLoadingIncidents, setIsLoadingIncidents] = useState(false);

    // Filter states
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterSeverity, setFilterSeverity] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');

    // Initial fetch
    useEffect(() => {
        loadIncidents();
    }, []);

    const loadIncidents = async () => {
        setIsLoadingIncidents(true);
        try {
            const data = await fetchIncidents();
            setIncidents(data.incidents || []);
        } catch (error) {
            console.error('Failed to load incidents:', error);
            // In a real app, show a toast here
        } finally {
            setIsLoadingIncidents(false);
        }
    };

    const handleUpload = async (file: File) => {
        setIsUploading(true);
        try {
            const { uploadId } = await uploadLog(file);
            const analysis = await analyzeLogs(uploadId);

            // Add new incidents to the list
            if (analysis.incidents && analysis.incidents.length > 0) {
                setIncidents(prev => [...analysis.incidents, ...prev]);
            }
        } catch (error) {
            console.error('Upload/Analysis failed:', error);
            alert('Failed to process log file. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    const handleTextAnalyze = async (logText: string) => {
        setIsUploading(true);
        try {
            const analysis = await analyzeLogs(undefined, logText);

            // Add new incidents to the list
            if (analysis.incidents && analysis.incidents.length > 0) {
                setIncidents(prev => [...analysis.incidents, ...prev]);
            }
        } catch (error) {
            console.error('Text analysis failed:', error);
            alert('Failed to analyze log text. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    const handleIncidentClick = (incident: Incident) => {
        setSelectedIncident(incident);
        setIsDrawerOpen(true);
    };

    const handleCloseDrawer = () => {
        setIsDrawerOpen(false);
        setTimeout(() => setSelectedIncident(null), 300); // Wait for animation
    };

    const handleResolve = (id: string) => {
        // Optimistic update
        setIncidents(prev => prev.map(inc =>
            inc.incidentId === id ? { ...inc, status: 'resolved' } : inc
        ));
        if (selectedIncident?.incidentId === id) {
            setSelectedIncident(prev => prev ? { ...prev, status: 'resolved' } : null);
        }
        // TODO: Call API to resolve
    };

    const handleReopen = (id: string) => {
        // Optimistic update
        setIncidents(prev => prev.map(inc =>
            inc.incidentId === id ? { ...inc, status: 'open' } : inc
        ));
        if (selectedIncident?.incidentId === id) {
            setSelectedIncident(prev => prev ? { ...prev, status: 'open' } : null);
        }
        // TODO: Call API to reopen
    };

    return (
        <Layout user={{ name: "Admin User", email: "admin@example.com" }} onLogout={onLogout}>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <div className="lg:col-span-1">
                    <LogUploader
                        onUpload={handleUpload}
                        onTextAnalyze={handleTextAnalyze}
                        isUploading={isUploading}
                    />
                </div>

                <div className="lg:col-span-3">
                    <IncidentList
                        incidents={incidents}
                        isLoading={isLoadingIncidents}
                        onIncidentClick={handleIncidentClick}
                        filterStatus={filterStatus}
                        setFilterStatus={setFilterStatus}
                        filterSeverity={filterSeverity}
                        setFilterSeverity={setFilterSeverity}
                        searchTerm={searchTerm}
                        setSearchTerm={setSearchTerm}
                    />
                </div>
            </div>

            <IncidentDrawer
                incident={selectedIncident}
                isOpen={isDrawerOpen}
                onClose={handleCloseDrawer}
                onResolve={handleResolve}
                onReopen={handleReopen}
            />
        </Layout>
    );
};
