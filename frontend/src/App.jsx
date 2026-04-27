import "./App.css";
import Globe from "./components/Globe";
import Navbar from "./components/Navbar";
import SidePanel from "./components/SidePanel";
import TransparencySidePanel from "./components/TransparencySidePanel";
import { useState } from "react";


function App() {
    const [selectedCountry, setSelectedCountry] = useState(null);
    return (
        <>
            <Navbar />
            <main className="app-main">
                <SidePanel selectedCountry={selectedCountry} />

                <div className="globe-wrapper">
                    <Globe setSelectedCountry={setSelectedCountry} />
                </div>

                <TransparencySidePanel />
            </main>
        </>
    );
}

export default App;
