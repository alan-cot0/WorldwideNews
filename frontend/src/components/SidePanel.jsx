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

// AI GENERATED: https://genai.umass.edu/share/MvjIEppqjGUUiJqtCbIub
function LoadNewsForCountry({ selectedCountry }) {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        setArticles([]);

        fetch(`http://127.0.0.1:8000/api/news/${countryToFips[selectedCountry]}`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                return response.json();
            })
            .then(data => {
                setArticles(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, [selectedCountry]);

    if (loading) return <p className="side-panel__status">Loading news...</p>;
    if (error) return <p className="side-panel__status">Failed to load news: {error}</p>;
    if (articles.length === 0) return <p className="side-panel__status">No articles found for this country.</p>;

    return (
        <table className="side-panel__news-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Headline</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
                {articles.map(article => (
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
                        <td>
                            <a
                                href={"https://" + new URL(article.url).hostname}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="side-panel__news-link">
                                    {new URL(article.url).hostname}
                            </a>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}
function SidePanelContent({ selectedCountry }) {
    return (
        <>
            <h3 className="side-panel__heading">News in </h3>
            <h2 className="side-panel__heading">{selectedCountry} </h2>
            <div className="side-panel__content">
                <LoadNewsForCountry selectedCountry={selectedCountry} />
            </div>{" "}
            {/* <h3 className="side-panel__heading">Intensity</h3>
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
            </div> */}
        </>
    );
}

function SidePanel({ isOpen, setIsOpen, selectedCountry }) {
    //const [isOpen, setIsOpen] = useState(false);

    return (
        <aside className={`side-panel${isOpen ? " side-panel--open" : ""}`} aria-label="Side panel">
            {/*
             * Body is fixed at the full open-width so content never
             * reflows mid-animation. overflow:hidden on the parent
             * clips it to the current animated width.
             */}
            <div className="side-panel__body">{isOpen && <SidePanelContent selectedCountry={selectedCountry} />}</div>
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
