export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type Status = 'open' | 'resolved';

export interface Incident {
    incidentId: string;
    createdAt: string;
    status: Status;
    severity: Severity;
    service: string;
    summary: string;
    rootCause: string;
    runbookSteps: string;
    lastUpdatedAt: string;
}

export interface LogUploadResponse {
    uploadId: string;
}

export interface AnalysisResponse {
    incidents: Incident[];
}

export interface User {
    email: string;
    name: string;
}

export interface AuthResponse {
    token: string;
    user: User;
}
