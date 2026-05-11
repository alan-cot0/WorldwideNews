import React, { useState } from "react";
import "./App.css";
import Globe from "./components/Globe";
import Navbar from "./components/Navbar";
import SidePanel from "./components/SidePanel";
import TransparencySidePanel from "./components/TransparencySidePanel";
//import { useState } from "react";


function App() {
    const [selectedCountry, setSelectedCountry] = useState(null);

    const [isOpen, setIsOpen] = useState(false);

    const [activeScoreAbout, setActiveScoreAbout] = useState(null);

    return (
        <>
            <Navbar 
                activeScoreAbout={activeScoreAbout} 
                setActiveScoreAbout={setActiveScoreAbout}/>
            <main className="app-main">

                <SidePanel isOpen={isOpen} setIsOpen={setIsOpen} selectedCountry={selectedCountry} onOpenScoring={() => setActiveScoreAbout("scoring")} />

                <div className="globe-wrapper">
                    <Globe onCountryClick={() => setIsOpen(true)}
                    onBackToGlobe={() => setIsOpen(false)} 
                    setSelectedCountry={setSelectedCountry} />
                </div>

                <TransparencySidePanel />
            </main>
        </>
    );
}

export default App;
