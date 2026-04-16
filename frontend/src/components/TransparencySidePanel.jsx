// Based on AI generated code - link in SidePanel.jsx

import { useState } from "react";
import "./TransparencySidePanel.css";

function TransparencySidePanelContent() {
    return (
        <>
            <h2 className="transparency-side-panel__heading">Our Mission & Methods</h2>
            <div className="transparency-side-panel__content">
                At WorldWide News we want to provide unbiased local news sourced from each country around the globe that frequently updates.
                To do this, we use GDELT 2.0 to source news and update our news output based on UTC. We believe that getting news from
                authentic local sources is the best way to get an accurate picture of other countries situations from around the world,
                and our platform is meant to help facilitate that. Additionally, we want our users to know that they are getting news
                from sources they can trust, which is why each article has a link to the source and a link to why we consider them
                trustworthy. If you want to read more about our process, click the about button in the navbar. For our ranking process for
                which articles we decide to display, click the scoring button.
            </div>{" "}

        </>
    );
}

function TransparencySidePanel({ children }) {
    const [isOpen, setIsOpen] = useState(true);

    return (
        <aside className={`transparency-side-panel${isOpen ? " transparency-side-panel--open" : ""}`} aria-label="Side panel">
            {/*
             * Body is fixed at the full open-width so content never
             * reflows mid-animation. overflow:hidden on the parent
             * clips it to the current animated width.
             */}
            <div className="transparency-side-panel__body">{isOpen && <TransparencySidePanelContent />}</div>

            {/* Toggle tab — always visible at the right edge of the panel */}
            <button
                className="transparency-side-panel__toggle"
                onClick={() => setIsOpen(v => !v)}
                aria-label={isOpen ? "Collapse panel" : "Expand panel"}
                aria-expanded={isOpen}
            >
                <span aria-hidden="true">{isOpen ? "›" : "‹"}</span>
            </button>
        </aside>
    );
}

export default TransparencySidePanel;
