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
                <div style={{ textIndent: '30px' }}>
                <p>WorldwideNews ranks articles separately for each country. When you select a country, the system looks at news 
                articles connected to that country and gives each article a relevancy score. That score is based on three signals: 
                Intensity, Richness, and Locality. </p>

                <p>Intensity measures how strong the article’s tone is. Articles with stronger positive or negative tone may receive a higher intensity score than more neutral articles. This uses tone and polarity data from GDELT.
                Richness measures how much context the article contains. Articles with more detected themes and named people receive a higher richness score because they give the system more information to evaluate.
                Locality measures how closely the article is connected to the selected country. Articles receive a higher locality score when more of their location mentions are tied to that country.
                </p>
                <p>
                The final relevancy score combines these three signals. By default, Intensity has the most influence, while Richness and Locality also contribute. 
                Users can adjust the sliders to change the ranking: increasing a slider makes that signal matter more, while lowering it makes that signal matter less.
                After articles are scored, WorldwideNews shows the top-ranked articles for the selected country. The ranking also tries to include some variety in topics, 
                so the list is not only the five highest-scoring articles from the same theme.
                </p>
                </div>
            </ScoreAbout>
        </>
    );
};

export default Navbar;