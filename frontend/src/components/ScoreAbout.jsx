import React, { useEffect } from "react";
import "./ScoreAbout.css";

const ScoreAbout = ({ isOpen, onClose, title, children }) => {
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        return () => { document.body.style.overflow = ""; };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="ScoreAbout-overlay">
            <button className="ScoreAbout-close" onClick={onClose}>&times;</button>
            <div className="ScoreAbout-body">
                <h1 className="ScoreAbout-title">{title}</h1>
                <div className="ScoreAbout-text">{children}</div>
            </div>
        </div>
    );
};

export default ScoreAbout;