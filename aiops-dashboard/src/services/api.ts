import type { Incident, LogUploadResponse, AnalysisResponse, AuthResponse } from '../types';

const API_BASE = '/api';

export const uploadLog = async (file: File): Promise<LogUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload-log`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${response.status} - ${errorText}`);
    }
    return response.json();
};

export const analyzeLogs = async (uploadId?: string, logText?: string): Promise<AnalysisResponse> => {
    const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uploadId, logText }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Analysis failed: ${response.status} - ${errorText}`);
    }
    return response.json();
};

export const fetchIncidents = async (status?: string, severity?: string): Promise<{ incidents: Incident[] }> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);

    const response = await fetch(`${API_BASE}/incidents?${params.toString()}`);
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch incidents: ${response.status} - ${errorText}`);
    }
    return response.json();
};

export const login = async (email: string, password: string): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Login failed: ${response.status} - ${errorText}`);
    }
    return response.json();
};
