import "./App.css";
import Globe from "./components/Globe";
import Navbar from "./components/Navbar";

function App() {
    return (
        <>
            <Navbar />
            <main style={{ paddingTop: "64px" }}>
                <Globe></Globe>
            </main>
        </>
    );
}

export default App;
