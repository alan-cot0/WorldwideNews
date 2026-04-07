// AI GENERATED: https://genai.umass.edu/share/6vjwQCoCH-kzh8jKxVP2E

import { useState } from "react";
import "./SidePanel.css";

function SidePanel({ children }) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <aside className={`side-panel${isOpen ? " side-panel--open" : ""}`} aria-label="Side panel">
            {/*
             * Body is fixed at the full open-width so content never
             * reflows mid-animation. overflow:hidden on the parent
             * clips it to the current animated width.
             */}
            <div className="side-panel__body">
                {isOpen && (
                    <>
                        <h2 className="side-panel__heading">News Panel</h2>
                        <div className="side-panel__content">{children}</div>
                    </>
                )}
            </div>

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
