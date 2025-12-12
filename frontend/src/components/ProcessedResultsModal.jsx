import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import ImageModal from './ImageModal';

const ProcessedResultsModal = ({ images, zipBlob, onClose }) => {
    const [selectedFullScreenImage, setSelectedFullScreenImage] = useState(null);

    const handleDownloadZip = () => {
        if (!zipBlob) return;
        const url = window.URL.createObjectURL(zipBlob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'processed_results.zip');
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
    };

    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                if (selectedFullScreenImage) {
                    setSelectedFullScreenImage(null);
                } else {
                    onClose();
                }
            }
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose, selectedFullScreenImage]);

    if (!images || images.length === 0) return null;

    return createPortal(
        <>
            <div className="modal-overlay" onClick={onClose} style={{ zIndex: 1050 }}>
                <div
                    className="modal-content"
                    onClick={e => e.stopPropagation()}
                    style={{
                        width: '90vw',
                        maxWidth: '1200px',
                        height: '90vh',
                        padding: 0,
                        overflow: 'hidden',
                        backgroundColor: 'var(--bg-dark)',
                        border: '1px solid var(--border)',
                        display: 'flex',
                        flexDirection: 'column',
                        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
                    }}
                >
                    <div className="flex" style={{
                        justifyContent: 'space-between',
                        padding: '2rem 2.5rem',
                        borderBottom: '1px solid var(--border)',
                        flexShrink: 0,
                        backgroundColor: 'var(--bg-dark)'
                    }}>
                        <div className="flex">
                            <h2 style={{ fontSize: '2rem', margin: 0 }}>Processed Results</h2>
                        </div>
                        <div className="flex">
                            {zipBlob && (
                                <button
                                    onClick={handleDownloadZip}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        fontSize: '0.9rem',
                                        background: 'var(--secondary)',
                                        marginRight: '1rem'
                                    }}
                                >
                                    Download ZIP 📥
                                </button>
                            )}
                            <button
                                className="modal-close"
                                onClick={onClose}
                                style={{ position: 'static', transform: 'none' }}
                            >
                                &times;
                            </button>
                        </div>
                    </div>

                    <div style={{ flex: 1, overflowY: 'auto', padding: '2.5rem' }}>
                        <div className="grid">
                            {images.map((img, index) => (
                                <div
                                    key={index}
                                    style={{
                                        backgroundColor: "var(--bg-card)",
                                        padding: "15px",
                                        borderRadius: "var(--radius)",
                                        border: "1px solid var(--border)",
                                        transition: "all 0.3s ease",
                                        cursor: "zoom-in",
                                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                    }}
                                    onClick={() => setSelectedFullScreenImage({ src: img.data, alt: img.name })}
                                    onMouseOver={(e) => {
                                        e.currentTarget.style.transform = "translateY(-5px)";
                                        e.currentTarget.style.borderColor = "var(--primary)";
                                    }}
                                    onMouseOut={(e) => {
                                        e.currentTarget.style.transform = "none";
                                        e.currentTarget.style.borderColor = "var(--border)";
                                    }}
                                >
                                    <div style={{ marginBottom: "0.75rem", fontSize: "1rem", fontWeight: "500", color: "var(--text-main)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                        {img.name}
                                    </div>
                                    <img
                                        src={img.data}
                                        alt={img.name}
                                        style={{ width: "100%", borderRadius: "8px", display: "block", aspectRatio: '16/9', objectFit: 'contain', backgroundColor: 'rgba(0,0,0,0.2)' }}
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <ImageModal
                image={selectedFullScreenImage}
                onClose={() => setSelectedFullScreenImage(null)}
            />
        </>,
        document.body
    );
};

export default ProcessedResultsModal;
