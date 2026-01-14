"use client";

import { useState, useCallback } from "react";

interface PDFUploaderProps {
    onUploadSuccess: (doc: { id: string; name: string }) => void;
}

export default function PDFUploader({ onUploadSuccess }: PDFUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const uploadFile = async (file: File) => {
        setIsUploading(true);
        setError(null);
        setUploadProgress(0);

        const formData = new FormData();
        formData.append("file", file);

        try {
            // Simulate progress for now
            const progressInterval = setInterval(() => {
                setUploadProgress((prev) => Math.min(prev + 10, 90));
            }, 200);

            const response = await fetch("http://localhost:8000/api/upload", {
                method: "POST",
                body: formData,
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                throw new Error("Upload failed");
            }

            const data = await response.json();
            setUploadProgress(100);

            onUploadSuccess({ id: data.document_id, name: file.name });

            // Reset after success
            setTimeout(() => {
                setUploadProgress(0);
                setIsUploading(false);
            }, 1000);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed. Is the backend running?");
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setIsDragging(false);

            const files = Array.from(e.dataTransfer.files);
            const pdfFile = files.find((f) => f.type === "application/pdf");

            if (pdfFile) {
                uploadFile(pdfFile);
            } else {
                setError("Please upload a PDF file");
            }
        },
        [onUploadSuccess]
    );

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            uploadFile(file);
        }
    };

    return (
        <div className="card p-8">
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <span className="text-3xl">📄</span> Upload Training Materials
            </h2>
            <p className="text-muted mb-6">
                Upload your firefighter exam PDFs. The AI will extract and index the content for study sessions.
            </p>

            {/* Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${isDragging
                        ? "border-fire-red bg-fire-red/10"
                        : "border-card-border hover:border-muted"
                    } ${isUploading ? "pointer-events-none opacity-60" : ""}`}
            >
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isUploading}
                />

                <div className="text-5xl mb-4">
                    {isUploading ? "⏳" : isDragging ? "📥" : "📁"}
                </div>

                <p className="text-lg font-semibold text-foreground mb-2">
                    {isUploading
                        ? "Processing document..."
                        : isDragging
                            ? "Drop your PDF here!"
                            : "Drag & drop a PDF here"}
                </p>
                <p className="text-sm text-muted">
                    or click to browse your files
                </p>

                {/* Progress Bar */}
                {isUploading && (
                    <div className="mt-6 max-w-xs mx-auto">
                        <div className="h-2 bg-card-border rounded-full overflow-hidden">
                            <div
                                className="h-full gradient-fire transition-all duration-300"
                                style={{ width: `${uploadProgress}%` }}
                            />
                        </div>
                        <p className="text-xs text-muted mt-2">{uploadProgress}% complete</p>
                    </div>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <div className="mt-4 p-4 bg-fire-red/20 border border-fire-red/50 rounded-lg text-fire-red">
                    <p className="font-semibold">⚠️ {error}</p>
                    <p className="text-sm mt-1 opacity-80">
                        Make sure the backend server is running on port 8000
                    </p>
                </div>
            )}

            {/* File Requirements */}
            <div className="mt-6 text-sm text-muted">
                <p className="font-medium text-foreground mb-2">Supported formats:</p>
                <ul className="list-disc list-inside space-y-1">
                    <li>PDF documents (textbooks, study guides, practice tests)</li>
                    <li>Maximum file size: 50MB</li>
                    <li>Text-based PDFs work best (scanned documents may have reduced accuracy)</li>
                </ul>
            </div>
        </div>
    );
}
