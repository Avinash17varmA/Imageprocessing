import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';

const ImageModal = ({ image, onClose }) => {
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose]);

    if (!image) return null;

    return createPortal(
        <div className="modal-overlay" onClick={onClose} style={{ zIndex: 2000 }}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>&times;</button>
                <img src={image.src} alt={image.alt || 'Full screen view'} />
            </div>
        </div>,
        document.body
    );
};

export default ImageModal;
