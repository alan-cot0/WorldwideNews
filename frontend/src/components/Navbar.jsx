import React, { useState, useCallback } from "react";
import ScoreAbout from "./ScoreAbout";
import "./Navbar.css";

const Navbar = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    const [activeScoreAbout, setActiveScoreAbout] = useState(null);

    const toggleMenu = useCallback((setting) => {
        if (setting !== undefined) {
            setMenuOpen(setting);
            return;
        }
        setMenuOpen((prev) => !prev);
    }, []);

    const openScoreAbout = (name) => {
        setActiveScoreAbout(name);
        setMenuOpen(false);
    };

    return (
        <>
            <nav className="navbar">
                <div className="navbar-container">
                    <div className="logo-container">
                        <img src="/new_logo.png" alt="logo" />
                        <div>
                            <a href="/" className="navbar-logo">
                                WorldWideNews
                            </a>
                            <p className="navbar-tagline">Transparency as a Priority</p>
                        </div>
                    </div>

                    <button
                        className={`hamburger ${menuOpen ? "active" : ""}`}
                        onClick={() => toggleMenu()}
                        aria-label="Toggle navigation"
                        aria-expanded={menuOpen}
                    >
                        <span className="bar" />
                        <span className="bar" />
                        <span className="bar" />
                    </button>

                    <ul className={`nav-links ${menuOpen ? "open" : ""}`}>
                        <li>
                            <button className="nav-button" onClick={() => openScoreAbout("about")}>
                                About
                            </button>
                        </li>
                        <li>
                            <button className="nav-button" onClick={() => openScoreAbout("scoring")}>
                                Scoring
                            </button>
                        </li>
                    </ul>
                </div>
            </nav>

            <ScoreAbout isOpen={activeScoreAbout === "about"} onClose={() => setActiveScoreAbout(null)} title="About">
                <p>One of the most common problems our customers have is how to use the word “about” correctly. 
                    This is particularly tricky because “about” is a common word and can be used in several contexts. 
                    We’ll run through a few of these uses here.
                    As a preposition, the word “about” can be used to link nouns and verbs, 
                    such as when using “about” to mean “concerning” or “on the subject of”:
                    We spoke about her neighbor’s awful choice of house paint.
                    However, a common mistake here is using “about” with “discussed.” This is incorrect: even though we ‘speak about’ something, 
                    the term “discuss” doesn’t require a preposition. As such, if we were to use “discussed” in the sentence above, 
                    it would simply be:
                    We discussed her neighbor’s awful choice of house paint.
                    About: Around on On One’s Person
                    We can also use it to mean “distributed around an area”:
                    In my town, there are several horribly painted houses about.
                    Or “on one’s person”:
                    She concealed the blue paint about her as she crept up on the house.</p>
            </ScoreAbout>

            <ScoreAbout isOpen={activeScoreAbout === "scoring"} onClose={() => setActiveScoreAbout(null)} title="Scoring">
                <p>It can also be used to allow materials to expand and contract under varying thermal conditions.
                     Scoring is used in place of cutting through the material all the way because you can obtain 
                     relatively the same results with less time and labor. However, when breaking along the score 
                     line the material may deviate from the set guideline, the back side of the break line often 
                     has a jagged edge to it from the shear fracture, and scoring offers very little use to metallic 
                     materials due to their malleability. Due to their hardness, tile, stone, glass, and ceramics respond 
                    well to scoring, and so the practice finds use in tile setting, stoneworking, glassblowing, and 
                    ceramics work respectively. Scoring is most commonly used in concrete work for decoration by making
                    the grooves appear to be grout lines from tile work. Confectioners often score hard candy such as 
                    butterscotch when batching it in sheets, in part because it avoids damaging the underlying baking tray.</p>
            </ScoreAbout>
        </>
    );
};

export default Navbar;