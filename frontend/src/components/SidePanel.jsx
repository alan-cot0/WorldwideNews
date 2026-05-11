// AI GENERATED: https://genai.umass.edu/share/6vjwQCoCH-kzh8jKxVP2E

import { useState, useEffect } from "react";
import "./SidePanel.css";
const countryToFips = {
    Zimbabwe: "ZI",
    Zambia: "ZA",
    Yemen: "YM",
    Vietnam: "VM",
    Venezuela: "VE",
    Vatican: "VT",
    Vanuatu: "NH",
    Uzbekistan: "UZ",
    Uruguay: "UY",

    Micronesia: "FM",
    "Marshall Is.": "RM",
    "N. Mariana Is.": "CQ",
    "U.S. Virgin Is.": "VQ",
    Guam: "GQ",
    "American Samoa": "AQ",
    "Puerto Rico": "RQ",
    "United States of America": "US",

    "S. Geo. and the Is.": "SX",
    "Br. Indian Ocean Ter.": "IO",
    "Saint Helena": "SH",
    "Pitcairn Is.": "PC",
    Anguilla: "AV",
    "Falkland Is.": "FK",
    "Cayman Is.": "CJ",
    Bermuda: "BD",
    "British Virgin Is.": "VI",
    "Turks and Caicos Is.": "TK",
    Montserrat: "MH",
    Jersey: "JE",
    Guernsey: "GK",
    "Isle of Man": "IM",

    "United Kingdom": "UK",
    "United Arab Emirates": "AE",
    Ukraine: "UP",
    Uganda: "UG",
    Turkmenistan: "TX",
    Turkey: "TU",
    Tunisia: "TS",
    "Trinidad and Tobago": "TD",
    Tonga: "TN",
    Togo: "TO",
    "Timor-Leste": "TT",
    Thailand: "TH",
    Tanzania: "TZ",
    Tajikistan: "TI",
    Taiwan: "TW",
    Syria: "SY",
    Switzerland: "SZ",
    Sweden: "SW",
    eSwatini: "WZ",
    Suriname: "NS",
    "S. Sudan": "OD",
    Sudan: "SU",
    "Sri Lanka": "CE",
    Spain: "SP",
    "South Korea": "KS",
    "South Africa": "SF",
    Somalia: "SO",
    Somaliland: null,

    "Solomon Is.": "BP",
    Slovakia: "LO",
    Slovenia: "SI",
    Singapore: "SN",
    "Sierra Leone": "SL",
    Seychelles: "SE",
    Serbia: "RB",
    Senegal: "SG",
    "Saudi Arabia": "SA",
    "São Tomé and Principe": "TP",
    "San Marino": "SM",
    Samoa: "WS",
    "St. Vin. and Gren.": "VC",
    "Saint Lucia": "ST",
    "St. Kitts and Nevis": "SC",

    Rwanda: "RW",
    Russia: "RS",
    Romania: "RO",
    Qatar: "QA",
    Portugal: "PO",
    Poland: "PL",
    Philippines: "RP",
    Peru: "PE",
    Paraguay: "PA",
    "Papua New Guinea": "PP",
    Panama: "PM",
    Palau: "PS",
    Pakistan: "PK",
    Oman: "MU",
    Norway: "NO",
    "North Korea": "KN",
    Nigeria: "NI",
    Niger: "NG",
    Nicaragua: "NU",
    "New Zealand": "NZ",
    "Cook Is.": "CW",

    Netherlands: "NL",
    Aruba: "AA",
    Curaçao: "UC",
    Nepal: "NP",
    Nauru: "NR",
    Namibia: "WA",
    Mozambique: "MZ",
    Morocco: "MO",
    "W. Sahara": "WI",
    Montenegro: "MJ",
    Mongolia: "MG",
    Moldova: "MD",
    Monaco: "MN",
    Mexico: "MX",
    Mauritius: "MP",
    Mauritania: "MR",
    Malta: "MT",
    Mali: "ML",
    Maldives: "MV",
    Malaysia: "MY",
    Malawi: "MI",
    Madagascar: "MA",
    Macedonia: "MK",
    Luxembourg: "LU",
    Lithuania: "LH",
    Liechtenstein: "LS",
    Libya: "LY",
    Liberia: "LI",
    Lesotho: "LT",
    Lebanon: "LE",
    Latvia: "LG",
    Laos: "LA",
    Kyrgyzstan: "KG",
    Kuwait: "KU",
    Kosovo: "KV",
    Kiribati: "KR",
    Kenya: "KE",
    Kazakhstan: "KZ",
    Jordan: "JO",
    Japan: "JA",
    Jamaica: "JM",
    Italy: "IT",
    Israel: "IS",
    Palestine: "GZ",
    Ireland: "EI",
    Iraq: "IZ",
    Iran: "IR",
    Indonesia: "ID",
    India: "IN",
    Iceland: "IC",
    Hungary: "HU",
    Honduras: "HO",
    Haiti: "HA",
    Guyana: "GY",
    "Guinea-Bissau": "PU",
    Guinea: "GV",
    Guatemala: "GT",
    Grenada: "GJ",
    Greece: "GR",
    Ghana: "GH",
    Germany: "GM",
    Georgia: "GG",
    Gambia: "GA",
    Gabon: "GB",
    France: "FR",
    Finland: "FI",
    Fiji: "FJ",
    Ethiopia: "ET",
    Estonia: "EN",
    Eritrea: "ER",
    "Equatorial Guinea": "EK",
    "El Salvador": "ES",
    Egypt: "EG",
    Ecuador: "EC",
    "Dominican Rep.": "DR",
    Dominica: "DO",
    Djibouti: "DJ",
    Denmark: "DA",
    Czechia: "EZ",
    Cyprus: "CY",
    Cuba: "CU",
    Croatia: "HR",
    "Côte d'Ivoire": "IV",
    "Costa Rica": "CS",
    "Dem. Rep. Congo": "CG",
    Congo: "CF",
    Comoros: "CN",
    Colombia: "CO",
    China: "CH",
    Chile: "CI",
    Chad: "CD",
    "Central African Rep.": "CT",
    "Cabo Verde": "CV",
    Canada: "CA",
    Cameroon: "CM",
    Cambodia: "CB",
    Myanmar: "BM",
    Burundi: "BY",
    "Burkina Faso": "UV",
    Bulgaria: "BU",
    Brunei: "BX",
    Brazil: "BR",
    Botswana: "BC",
    "Bosnia and Herz.": "BK",
    Bolivia: "BL",
    Bhutan: "BT",
    Benin: "BN",
    Belize: "BH",
    Belgium: "BE",
    Belarus: "BO",
    Barbados: "BB",
    Bangladesh: "BG",
    Bahrain: "BA",
    Bahamas: "BF",
    Azerbaijan: "AJ",
    Austria: "AU",
    Australia: "AS",
    Armenia: "AM",
    Argentina: "AR",
    "Antigua and Barb.": "AC",
    Angola: "AO",
    Andorra: "AN",
    Algeria: "AG",
    Albania: "AL",
    Afghanistan: "AF",
    Antarctica: "AY",
};

const API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_WEIGHTS = {
    weight_intensity: 0.4,
    weight_richness: 0.3,
    weight_locality: 0.3,
};

function NewsTable({ articles, loading, error }) {
    if (loading) return <p className="side-panel__status">Loading news...</p>;
    if (error) return <p className="side-panel__status">Failed to load news: {error}</p>;
    if (articles.length === 0) return <p className="side-panel__status">No articles found for this country.</p>;

    return (
        <table className="side-panel__news-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Headline</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
                {articles.map((article) => (
                    <tr key={article.rank}>
                        <td>{article.rank}</td>
                        <td>
                            <a
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="side-panel__news-link"
                            >
                                {article.headline}
                            </a>
                        </td>
                        <td>{article.source_name || new URL(article.url).hostname}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

function WeightSlider({ label, value, onChange, disabled }) {
    return (
        <label className="side-panel__slider">
            <span className="side-panel__slider-label">
                {label}
                <span>{Math.round(value * 100)}%</span>
            </span>
            <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={value}
                disabled={disabled}
                onChange={(event) => onChange(Number(event.target.value))}
            />
        </label>
    );
}

// AI GENERATED: https://genai.umass.edu/share/MvjIEppqjGUUiJqtCbIub
function SidePanelContent({ selectedCountry, onOpenScoring }) {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState(null);
    const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
    const [hasUserChangedWeights, setHasUserChangedWeights] = useState(false);
    const countryCode = countryToFips[selectedCountry];

    useEffect(() => {
        if (!countryCode) {
            setArticles([]);
            setError("No country code is mapped for this location.");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);
        setArticles([]);
        setWeights(DEFAULT_WEIGHTS);
        setHasUserChangedWeights(false);

        fetch(`${API_BASE_URL}/api/news/${countryCode}`)
            .then((response) => {
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                return response.json();
            })
            .then(data => {
                setArticles(data);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, [countryCode]);

    useEffect(() => {
        if (!countryCode || loading || !hasUserChangedWeights) return;

        const controller = new AbortController();
        const timeout = window.setTimeout(() => {
            setUpdating(true);
            setError(null);

            fetch(`${API_BASE_URL}/api/scoring/${countryCode}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(weights),
                signal: controller.signal,
            })
                .then((response) => {
                    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                    return response.json();
                })
                .then((data) => {
                    setArticles(data.articles || []);
                    setUpdating(false);
                })
                .catch((err) => {
                    if (err.name === "AbortError") return;
                    setError(err.message);
                    setUpdating(false);
                });
        }, 400);

        return () => {
            controller.abort();
            window.clearTimeout(timeout);
        };
    }, [countryCode, weights, loading, hasUserChangedWeights]);

    const setWeight = (key, value) => {
        setHasUserChangedWeights(true);
        setWeights((current) => ({ ...current, [key]: value }));
    };

    return (
        <>
            <h3 className="side-panel__heading">News in </h3>
            <h2 className="side-panel__heading">{selectedCountry} </h2>
            <div className="side-panel__content">
                <NewsTable articles={articles} loading={loading || updating} error={error} />
            </div>


            <div style={{ marginTop: "24px", marginBottom: "-4px", textAlign: "right" }}>
                <button 
                    className="side-panel__scoring-link" 
                    onClick={onOpenScoring}
                >
                    How Our Scoring Works
                </button>
            </div>


            <div className="side-panel__controls" aria-label="Scoring weights">
                <WeightSlider
                    label="Intensity"
                    value={weights.weight_intensity}
                    disabled={!countryCode}
                    onChange={(value) => setWeight("weight_intensity", value)}
                />
                <WeightSlider
                    label="Richness"
                    value={weights.weight_richness}
                    disabled={!countryCode}
                    onChange={(value) => setWeight("weight_richness", value)}
                />
                <WeightSlider
                    label="Locality"
                    value={weights.weight_locality}
                    disabled={!countryCode}
                    onChange={(value) => setWeight("weight_locality", value)}
                />
            </div>
        </>
    );
}

function SidePanel({ isOpen, setIsOpen, selectedCountry, onOpenScoring}) {
    //const [isOpen, setIsOpen] = useState(false);

    return (
        <aside className={`side-panel${isOpen ? " side-panel--open" : ""}`} aria-label="Side panel">
            {/*
             * Body is fixed at the full open-width so content never
             * reflows mid-animation. overflow:hidden on the parent
             * clips it to the current animated width.
             */}
            <div className="side-panel__body">{isOpen && <SidePanelContent selectedCountry={selectedCountry} onOpenScoring={onOpenScoring} />}</div>
            {/* Toggle tab — always visible at the right edge of the panel */}
            <button
                className="side-panel__toggle"
                onClick={() => setIsOpen(!isOpen)}
                aria-label={isOpen ? "Collapse panel" : "Expand panel"}
                aria-expanded={isOpen}
            >
                <span aria-hidden="true">{isOpen ? "‹" : "›"}</span>
            </button>
        </aside>
    );
}

export default SidePanel;
