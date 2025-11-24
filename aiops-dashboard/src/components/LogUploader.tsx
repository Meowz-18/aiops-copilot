import React, { useCallback, useState } from 'react';
import { Upload, FileText, Loader2, MessageSquare } from 'lucide-react';

interface LogUploaderProps {
    onUpload: (file: File) => Promise<void>;
    onTextAnalyze: (text: string) => Promise<void>;
    isUploading: boolean;
}

export const LogUploader: React.FC<LogUploaderProps> = ({ onUpload, onTextAnalyze, isUploading }) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [inputMode, setInputMode] = useState<'file' | 'text'>('file');
    const [logText, setLogText] = useState('');

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setSelectedFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUploadClick = () => {
        if (inputMode === 'file' && selectedFile) {
            onUpload(selectedFile);
        } else if (inputMode === 'text' && logText.trim()) {
            onTextAnalyze(logText);
        }
    };

    const canSubmit = (inputMode === 'file' && selectedFile) || (inputMode === 'text' && logText.trim());

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Log Ingestion
            </h2>

            {/* Toggle between File and Text */}
            <div className="flex gap-2 mb-4">
                <button
                    onClick={() => setInputMode('file')}
                    className={`flex-1 py-2 px-4 rounded-md flex items-center justify-center gap-2 font-medium transition-colors ${inputMode === 'file'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                >
                    <Upload className="w-4 h-4" />
                    Upload File
                </button>
                <button
                    onClick={() => setInputMode('text')}
                    className={`flex-1 py-2 px-4 rounded-md flex items-center justify-center gap-2 font-medium transition-colors ${inputMode === 'text'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                >
                    <MessageSquare className="w-4 h-4" />
                    Paste Text
                </button>
            </div>

            {/* File Upload  Mode */}
            {inputMode === 'file' && (
                <div
                    className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={handleChange}
                        disabled={isUploading}
                        accept=".log,.txt,.csv"
                    />

                    <div className="flex flex-col items-center gap-2 pointer-events-none">
                        <Upload className={`w-8 h-8 ${selectedFile ? 'text-blue-600' : 'text-gray-400'}`} />
                        {selectedFile ? (
                            <div className="text-sm">
                                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                                <p className="text-gray-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                            </div>
                        ) : (
                            <div className="text-sm text-gray-500">
                                <p className="font-medium text-gray-900">Drop log file here</p>
                                <p>or click to browse</p>
                                <p className="text-xs mt-1">Supports: .log, .txt, .csv</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Text Input Mode */}
            {inputMode === 'text' && (
                <div>
                    <textarea
                        className="w-full h-48 p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none font-mono text-sm"
                        placeholder="Paste your server logs here...&#10;&#10;Example:&#10;192.168.1.1 - - [24/Nov/2025:10:15:30 +0000] GET /api/users 500&#10;192.168.1.2 - - [24/Nov/2025:10:15:31 +0000] GET /api/users 500&#10;192.168.1.3 - - [24/Nov/2025:10:15:32 +0000] GET /api/users 500"
                        value={logText}
                        onChange={(e) => setLogText(e.target.value)}
                        disabled={isUploading}
                    />
                    <p className="text-xs text-gray-500 mt-2">
                        {logText.split('\n').length} lines • {logText.length} characters
                    </p>
                </div>
            )}

            <button
                onClick={handleUploadClick}
                disabled={!canSubmit || isUploading}
                className={`mt-4 w-full py-2 px-4 rounded-md flex items-center justify-center gap-2 font-medium transition-colors ${!canSubmit || isUploading
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
            >
                {isUploading ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Analyzing...
                    </>
                ) : (
                    <>Analyze Logs</>
                )}
            </button>
        </div>
    );
};
