import React, { useState, useCallback } from "react";
import ScoreAbout from "./ScoreAbout";
import "./Navbar.css";

const Navbar = ({activeScoreAbout, setActiveScoreAbout}) => {
    const [menuOpen, setMenuOpen] = useState(false);
    //const [activeScoreAbout, setActiveScoreAbout] = useState(null);

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
                <div style={{ textIndent: '30px' }}>
                <p>WorldWide News is a platform in which users can click on any country on the globe and browse the top local articles
                    from that country each day. All countries are accessible by dragging the globe to view them and zooming in to click
                    if they are too small to see well from the full view. Once a country is clicked, a sidebar with the top 5 article headlines
                    for that country will appear, and the user can click the links for each article to go to its source and read more.
                    Additionally, adjustable sliders appear under the articles, which can be used to change the users preference of types
                    of articles that appear. The sliders meanings, functionality, and algorithm are explained in depth on the Scoring page.
                </p>
                <p>WorldWide News seeks to provide transparent, unbiased, accessible and local news from around the world. To provide transparency,
                    all of our practices are documented on this website. To be unbiased and local, we source our news from <a href="https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/" target="_blank" rel="noopener noreferrer" style={{ textIndent: 0, display: 'inline-block' }}>
                        GDELT 2.0
                    </a>
                    , a trusted news API 
                    that provides news from local sources all over the world. Additionally, users can filter news on what they would like to see,
                    giving them agency in what they consume. Our accessibility goals include providing contrasting colors and high readability on the website,
                    along with a clear UI that can help uninformed users navigate the website with ease.
                </p>
                <p>GDELT provides news that constantly updates. Our website pulls news from GDELT every few minutes, which is already assigned for each country,
                    sorts it and ranks it, and sends the top ~100 articles to the client which are cached. These articles are updated on the client side
                    every 10-12 hours based on UTC, a world standard time zone, and can be reranked by the client at will. This provides fresh yet
                    complete news since time is allowed for smaller countries to get news. If no news come out from a certain country in that time span, 
                    the most recent news is displayed until new news are released.
                </p>
                <p> On the UI side, WorldWide News hopes to provide a highly readable, easy to navigate, and self explanatory website. Furthermore,
                    we hope to avoid issues with red-green colorblindness with our color scheme and use text that is bold and clear. With all of this in 
                    combination, we have hopefully delivered a product that upholds the values of our team.
                </p>
                </div>
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