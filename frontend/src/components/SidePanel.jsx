// AI GENERATED: https://genai.umass.edu/share/6vjwQCoCH-kzh8jKxVP2E

import { useState } from "react";
import "./SidePanel.css";

function SidePanelContent() {
    return (
        <>
            <h2 className="side-panel__heading">News Panel</h2>
            <div className="side-panel__content">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
                dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
                ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
                fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
                deserunt mollit anim id est laborum.
            </div>{" "}
            <h3 className="side-panel__heading">Intensity</h3>
            <div className="side-panel__content">
                <input type="range"></input>
            </div>
            <h3 className="side-panel__heading">Richness</h3>
            <div className="side-panel__content">
                <input type="range"></input>
            </div>
            <h3 className="side-panel__heading">Locality</h3>
            <div className="side-panel__content">
                <input type="range"></input>
            </div>
        </>
    );
}

function SidePanel({ children }) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <aside className={`side-panel${isOpen ? " side-panel--open" : ""}`} aria-label="Side panel">
            {/*
             * Body is fixed at the full open-width so content never
             * reflows mid-animation. overflow:hidden on the parent
             * clips it to the current animated width.
             */}
            <div className="side-panel__body">{isOpen && <SidePanelContent />}</div>

            {/* Toggle tab — always visible at the right edge of the panel */}
            <button
                className="side-panel__toggle"
                onClick={() => setIsOpen(v => !v)}
                aria-label={isOpen ? "Collapse panel" : "Expand panel"}
                aria-expanded={isOpen}
            >
                <span aria-hidden="true">{isOpen ? "‹" : "›"}</span>
            </button>
        </aside>
    );
}

export default SidePanel;
