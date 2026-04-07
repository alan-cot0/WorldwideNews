import "./App.css";
import Globe from "./components/Globe";
import Navbar from "./components/Navbar";
import SidePanel from "./components/SidePanel";

function App() {
    return (
        <>
            <Navbar />
            <main className="app-main">
                <SidePanel>
                    {/* Drop your news-feed / filter content here */}
                    <p>Your panel content goes here.</p>
                </SidePanel>

                <div className="globe-wrapper">
                    <Globe />
                </div>
            </main>
        </>
    );
}

export default App;