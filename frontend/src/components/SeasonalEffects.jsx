import React, { useEffect, useState } from 'react';
import './SeasonalEffects.css';

const SeasonalEffects = () => {
    const [season, setSeason] = useState('');

    useEffect(() => {
        const month = new Date().getMonth(); // 0-11

        // Winter: Nov (10), Dec (11), Jan (0), Feb (1)
        if (month === 10 || month === 11 || month === 0 || month === 1) {
            setSeason('winter');
        }
        // Summer: Mar (2), Apr (3), May (4), Jun (5)
        else if (month >= 2 && month <= 5) {
            setSeason('summer');
        }
        // Rainy: Jul (6), Aug (7), Sep (8), Oct (9)
        else {
            setSeason('rainy');
        }
    }, []);

    const renderParticles = (type, count = 50) => {
        const particles = [];
        for (let i = 0; i < count; i++) {
            const style = {
                left: `${Math.random() * 100}vw`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${Math.random() * 2 + (type === 'rain' ? 0.5 : 3)}s`,
                opacity: Math.random() * 0.5 + 0.3
            };
            particles.push(<div key={i} className={`particle ${type}`} style={style}></div>);
        }
        return <div className="seasonal-container">{particles}</div>;
    };

    if (season === 'winter') {
        return renderParticles('snow', 50);
    } else if (season === 'rainy') {
        return renderParticles('rain', 100);
    } else if (season === 'summer') {
        return (
            <div className="seasonal-container summer-container">
                <div className="sun-shine"></div>
                <div className="light-ray"></div>
            </div>
        );
    }

    return null;
};

export default SeasonalEffects;
