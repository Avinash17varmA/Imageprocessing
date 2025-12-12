import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

const CameraModal = ({ onClose, onCapture }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [error, setError] = useState('');
    const [stream, setStream] = useState(null);

    useEffect(() => {
        startCamera();
        return () => stopCamera();
    }, []);

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user' }
            });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
            setError("Could not access camera. Please ensure permissions are granted.");
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    const handleCapture = () => {
        if (videoRef.current && canvasRef.current) {
            const video = videoRef.current;
            const canvas = canvasRef.current;

            // Set canvas dimensions to match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Draw video frame to canvas
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert to blob
            canvas.toBlob((blob) => {
                if (blob) {
                    // Create a File object
                    const file = new File([blob], `capture_${Date.now()}.png`, { type: "image/png" });
                    onCapture(file);
                    handleClose();
                }
            }, 'image/png');
        }
    };

    const handleClose = () => {
        stopCamera();
        onClose();
    };

    return createPortal(
        <div className="modal-overlay" onClick={handleClose}>
            <div
                className="modal-content"
                onClick={e => e.stopPropagation()}
                style={{
                    backgroundColor: 'var(--bg-dark)',
                    padding: '2rem',
                    width: '90vw',
                    maxWidth: '600px',
                    textAlign: 'center'
                }}
            >
                <h2 className="mb-4">Take a Photo</h2>

                {error ? (
                    <div style={{ color: '#ff6b6b', marginBottom: '1rem' }}>{error}</div>
                ) : (
                    <div style={{
                        position: 'relative',
                        width: '100%',
                        maxWidth: '500px',
                        margin: '0 auto',
                        borderRadius: 'var(--radius)',
                        overflow: 'hidden',
                        backgroundColor: '#000',
                        aspectRatio: '4/3'
                    }}>
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                    </div>
                )}

                <canvas ref={canvasRef} style={{ display: 'none' }} />

                <div className="flex" style={{ justifyContent: 'center', marginTop: '2rem', gap: '1rem' }}>
                    <button
                        onClick={handleClose}
                        style={{ background: 'var(--bg-input)', color: 'var(--text-muted)' }}
                    >
                        Cancel
                    </button>
                    {!error && (
                        <button onClick={handleCapture}>
                            Capture 📸
                        </button>
                    )}
                </div>
            </div>
        </div>,
        document.body
    );
};

export default CameraModal;
