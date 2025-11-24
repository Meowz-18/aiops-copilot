import React, { useCallback, useState } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';

interface LogUploaderProps {
    onUpload: (file: File) => Promise<void>;
    isUploading: boolean;
}

export const LogUploader: React.FC<LogUploaderProps> = ({ onUpload, isUploading }) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

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
        if (selectedFile) {
            onUpload(selectedFile);
        }
    };

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Log Ingestion
            </h2>

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
                        </div>
                    )}
                </div>
            </div>

            <button
                onClick={handleUploadClick}
                disabled={!selectedFile || isUploading}
                className={`mt-4 w-full py-2 px-4 rounded-md flex items-center justify-center gap-2 font-medium transition-colors ${!selectedFile || isUploading
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
            >
                {isUploading ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Uploading...
                    </>
                ) : (
                    'Upload & Analyze'
                )}
            </button>
        </div>
    );
};
