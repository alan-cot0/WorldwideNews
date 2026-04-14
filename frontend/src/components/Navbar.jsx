// AI GENERATED: https://genai.umass.edu/share/qZzhcGQtJ0F2o79SdiI1F

import React, { useState } from "react";
import "./Navbar.css";

const Navbar = () => {
    const [menuOpen, setMenuOpen] = useState(false);

    const toggleMenu = useCallback((setting) => {
        if (setting !== undefined) {
            setMenuOpen(prev => !prev);
            return;
        }
        setMenuOpen(setting);
    }, []);

    return (
        <nav className="navbar">
            <div className="navbar-container">
                {/* Brand / Logo */}
                <div className="logo-container">
                    <img src="../../public/new_logo.png"></img>
                    <div>
                    <a href="/" className="navbar-logo">
                        WorldWideNews
                    </a>
                    <p className="navbar-tagline">Transparency as a Priority</p>
                    </div>
                </div>
                {/* Hamburger Icon (mobile) */}
                <button
                    className={`hamburger ${menuOpen ? "active" : ""}`}
                    onClick={toggleMenu}
                    aria-label="Toggle navigation"
                    aria-expanded={menuOpen}
                >
                    <span className="bar" />
                    <span className="bar" />
                    <span className="bar" />
                </button>

                {/* Nav Links */}
                <ul className={`nav-links ${menuOpen ? "open" : ""}`}>
                    <li>
                        <a href="#services" onClick={() => setMenuOpen(false)}>
                            About
                        </a>
                    </li>
                    <li>
                        <a href="#contact" onClick={() => setMenuOpen(false)}>
                            Scoring
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navbar;
