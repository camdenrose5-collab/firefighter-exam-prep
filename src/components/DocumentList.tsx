"use client";

interface Document {
    id: string;
    name: string;
    uploadedAt: string;
}

interface DocumentListProps {
    documents: Document[];
}

export default function DocumentList({ documents }: DocumentListProps) {
    return (
        <div className="card p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>📚</span> Your Documents
            </h3>

            {documents.length === 0 ? (
                <div className="text-center py-8">
                    <div className="text-4xl mb-3 opacity-50">📭</div>
                    <p className="text-muted text-sm">No documents uploaded yet</p>
                    <p className="text-muted text-xs mt-1">
                        Upload a PDF to get started
                    </p>
                </div>
            ) : (
                <ul className="space-y-3">
                    {documents.map((doc) => (
                        <li
                            key={doc.id}
                            className="p-3 bg-card-border/50 rounded-lg hover:bg-card-border transition-colors"
                        >
                            <div className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded bg-fire-red/20 flex items-center justify-center flex-shrink-0">
                                    <span className="text-fire-red text-sm">PDF</span>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-sm truncate" title={doc.name}>
                                        {doc.name}
                                    </p>
                                    <p className="text-xs text-muted mt-0.5">
                                        {new Date(doc.uploadedAt).toLocaleTimeString()}
                                    </p>
                                </div>
                                <div className="w-2 h-2 rounded-full bg-green-500 mt-2" title="Indexed" />
                            </div>
                        </li>
                    ))}
                </ul>
            )}

            {documents.length > 0 && (
                <div className="mt-4 pt-4 border-t border-card-border">
                    <p className="text-xs text-muted text-center">
                        ✅ {documents.length} document{documents.length !== 1 ? "s" : ""} ready for study
                    </p>
                </div>
            )}
        </div>
    );
}
