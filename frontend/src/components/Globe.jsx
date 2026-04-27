import React, { useEffect, useRef, useState, useCallback, forceUpdate } from "react";
import * as d3 from "d3";

// This is the dataset that holds the country boundaries and globe data
import * as topojson from "topojson-client";

// Used for dragging and calculating appearance of 3D globe
import versor from "versor";

/** Zoom state enum */
const ZState = Object.freeze({
    NotZoomed: 0,
    ZoomingIn: 1,
    Zoomed: 2,
    ZoomingOut: 3,
});

// initial globe size
const INITIAL_SCALE = 300;

const Globe = ({setSelectedCountry}) => {
    // console.log("react rendering globe component");
    const canvasRef = useRef(null);
    // const goBackButtonRef = useRef(null);
    const [displayGoBack, setDisplayGoBack] = useState(false);

    //data is used to contain land shapes, borders, and country lists
    const [data, setData] = useState(null);

    //stores current selected country by user
    const activeCountry = useRef(null);

    //checking which country mouse is hovering over
    const hoveredCountry = useRef(null);

    /** if user is currently zoomed in on a country where the news will pop up */
    const zoomState = useRef(ZState.NotZoomed);

    //if true user is currently dragging the globe
    const [isDragging, setIsDragging] = useState(false);

    // "destination" zoom level when country is not selected, can be used to smooth zooming in and out (not implemented)
    const [targetZoom , setTargetZoom] = useState(INITIAL_SCALE); // change to ref?

    //set dimensions to fill screen
    const [dimensions, setDimensions] = useState({
        width: window.innerWidth,
        height: window.innerHeight,
    });

    //creates the 3D globe
    const projection = useRef(
        d3.geoOrthographic().scale(INITIAL_SCALE) // initialize with globe size
    );

    // resize globe on window resize
    useEffect(() => {
        const handleResize = () => {
            console.log("resizing");
            const w = window.innerWidth;
            const h = window.innerHeight;
            setDimensions({ width: w, height: h });
            projection.current.translate([w / 2, h / 2]);
        };
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);
    
    //loads all the topojson data
    useEffect(() => {
        Promise.all([
            d3.json("/data/countries-50m.json"), //more detailed countries used when view is static
            d3.json("/data/countries-110m.json"), //less detailed countries used when dragging for performance
        ]).then(([world50, world110]) => {
            setData({
                //extracts country shapes from data
                land50: topojson.feature(world50, world50.objects.land),
                land110: topojson.feature(world110, world110.objects.land),

                //extracts country borders from data
                borders50: topojson.mesh(world50, world50.objects.countries, (a, b) => a !== b), //(a, b) => a !== b removed to add outer borders
                borders110: topojson.mesh(world110, world110.objects.countries, (a, b) => a !== b), //(a, b) => a !== b removed to add outer borders

                outborders50: topojson.mesh(world50, world50.objects.countries, (a, b) => a == b),
                outborders110: topojson.mesh(world110, world110.objects.countries, (a, b) => a == b),

                //array of country shapes
                countries: topojson.feature(world50, world50.objects.countries).features,
            });
        });
    }, []);

    /** draws the globe, gets called when view changes
     * @param lowRes if true, uses lower resolution data for faster rendering (used when rendering many frames in succession)
     */
    const render = useCallback((lowRes = false) => {
        // console.log("rendering", { lowRes });
        const canvas = canvasRef.current;
        if (!canvas || !data) return;

        const w = canvas.width, h = canvas.height;
        //initializes canvas which allows for drawing borders
        const context = canvas.getContext("2d");

        projection.current.translate([w / 2, h / 2]);
        // console.log("current scale", projection.current.scale());
        if (zoomState.current === ZState.NotZoomed && projection.current.scale() > 900)
            lowRes = false; //if zoomed in, override to high res

        //d3 function that converts coordinates to canvas shapes
        const path = d3.geoPath(projection.current, context);

        //when dragging use lower res data
        const land = lowRes ? data.land110 : data.land50;
        const borders = lowRes ? data.borders110 : data.borders50;
        const outborders = lowRes ? data.outborders110 : data.outborders50;

        //when changing frames, this erases previous frames to make way for new ones
        context.clearRect(0, 0, w, h);

        //makes the entire globe ocean colored
        context.beginPath();
        path({ type: "Sphere" });
        context.fillStyle = "#2b6cb0";
        context.fill();

        //fills in all land objects green
        context.beginPath();
        path(land);
        context.fillStyle = "#38a169";
        context.fill();

        //draws borders between countries
        context.beginPath();
        path(borders);
        context.strokeStyle = "#ffffff";
        context.lineWidth = 0.9;
        context.stroke();

        context.beginPath();
        path(outborders);
        context.strokeStyle = "#e9e9e9";
        context.lineWidth = 0.5;
        context.stroke();

        //if a country is selected, highlight it
        if (activeCountry.current) {
            context.beginPath();
            path(activeCountry.current);
            context.fillStyle = "#f6ad55";
            context.fill();
            context.strokeStyle = "#ffffff";
            context.lineWidth = 1;
            context.stroke();
            // console.log(zoomState.current);
            //adds name of country when zoomed in
            if (zoomState.current > 0) {
                const centroid = projection.current(d3.geoCentroid(activeCountry.current));
                context.fillStyle = "#000000";
                context.font = "bold 20px Arial";
                context.textAlign = "center";
                context.shadowBlur = 4;
                context.shadowColor = "white";
                context.fillText(activeCountry.current.properties.name, centroid[0], centroid[1] - 20);
                context.shadowBlur = 0;
            }
        } else {
            //highlight/distinguish hovered country
            if (hoveredCountry.current && hoveredCountry.current !== activeCountry.current) {
                context.beginPath();
                path(hoveredCountry.current);
                context.fillStyle = "rgba(255, 255, 255, 0.3)"; // Subtle white overlay
                context.fill();
            }
            
            //add hovered countries name
            const countryToLabel = hoveredCountry.current;
            if (countryToLabel) {
                const centroid = projection.current(d3.geoCentroid(countryToLabel));
                if (centroid) { //checks if country is visible before highlighting and showing name
                    context.fillStyle = "#000000";
                    context.font = "bold 16px Arial";
                    context.textAlign = "center";
                    context.shadowBlur = 4;
                    context.shadowColor = "white";
                    context.fillText(countryToLabel.properties.name, centroid[0], centroid[1]);
                    context.shadowBlur = 0;
                }
            }
        }
    }, [data, dimensions]);
    useEffect(() => { console.log("render updated"); render(true); }, [render]);

    // set up canvas event handlers
    useEffect(() => {
        console.log("setting event handlers");
        if (!data || !canvasRef.current) return;

        const canvas = d3.select(canvasRef.current);

        //makes the user unable to move while in country view
        canvas.on(".drag", null).on(".zoom", null);

        //zoom functionality
        const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .filter(event => zoomState.current === ZState.NotZoomed && (event.type === 'wheel' || (event.touches && event.touches.length > 1)) )
            .on("zoom", (event) => {
                setTargetZoom(INITIAL_SCALE * event.transform.k);
                projection.current.scale(INITIAL_SCALE * event.transform.k);
                render(true);
            })
            .on("end", () => {
                render(false);
            });

        // disables default behavior?
        canvas.call(zoom).on("mousedown.zoom", null).on("touchstart.zoom", null);

        let v0, q0, r0;
        //d3.drag handles the dragging motion
        const drag = d3.drag()
            .filter(() => zoomState.current === ZState.NotZoomed) //only allow dragging when not zoomed in
            .on("start", event => {
                setIsDragging(true);

                v0 = versor.cartesian(projection.current.invert([event.x, event.y])); //stores starting vector
                q0 = versor((r0 = projection.current.rotate())); //updates globe based on user input
            })
            .on("drag", event => {
                const v1 = versor.cartesian(projection.current.rotate(r0).invert([event.x, event.y]));
                projection.current.rotate(versor.rotation(versor.multiply(q0, versor.delta(v0, v1))));

                //low resolution during drag
                render(true);
            })
            .on("end", () => {
                setIsDragging(false);
                render(false);
            });
        canvas.call(drag);

        //track mouse hovering
        const timer = d3.timer(() => timer.stop());
        canvas.on("mousemove", (event) => {
            if (zoomState.current !== ZState.NotZoomed) return; //don't update hovered country when zoomed in
            const [mouseX, mouseY] = d3.pointer(event);
            const coords = projection.current.invert([mouseX, mouseY]);
            const country = coords && data.countries.find(f => d3.geoContains(f, coords));
            if (country !== hoveredCountry.current) {
                hoveredCountry.current = country;
                // console.log("changing country hover");
                render(true);
                timer.restart((t) => {
                    render(false);
                    timer.stop();
                    console.log("timer stopped");
                }, 200);
            }
        });

        canvas.on("mouseleave", () => hoveredCountry.current = null);

        canvas.on("click", event => {
            console.log("click", { zoomState: zoomState.current });
            //if the user is already zoomed on a country, nothing happens
            if (zoomState.current !== ZState.NotZoomed) return;

            //checks coordinate of user click
            const p = projection.current.invert(d3.pointer(event));
            //converts that coordinate to a country if the click is within a country
            const country = data.countries.find(f => d3.geoContains(f, p));
            if (!country) return; // if user clicks on ocean, do nothing

            //stop name hovering
            hoveredCountry.current = null;

            //if its in a country, choose that country
            activeCountry.current = country;
            console.log("active country", activeCountry.current.properties.name);
            setSelectedCountry(activeCountry.current.properties.name);
            setDisplayGoBack(true);

            //toggle being zoomed in
            zoomState.current = ZState.ZoomingIn;

            //d3 function to find country center
            const centroid = d3.geoCentroid(country);

            //d3 function to get country size
            const bounds = d3.geoBounds(country);

            //dx gets width of country, dy gets height
            const dx = bounds[1][0] - bounds[0][0];
            const dy = bounds[1][1] - bounds[0][1];

            //longitude is calculated 180 to -180, so when crossing the dateline there can be large jumps
            //this function fixes for that by converting to positive
            const trueDx = dx < 0 ? dx + 360 : dx;
            const maxDim = Math.max(trueDx, dy);

            //sets zoom in limit (DISTINCT FROM targetZoom)
            const targetScale = Math.max(INITIAL_SCALE, Math.min(3000, (dimensions.width / maxDim) * 23));

            d3.transition()
                .duration(1200)
                .tween("zoom", () => {
                    //rotates globe to country while zooming
                    //zooms in over time
                    const r = d3.interpolate(projection.current.rotate(), [-centroid[0], -centroid[1], 0]);
                    const s = d3.interpolate(projection.current.scale(), targetScale);
                    return t => {
                        projection.current.rotate(r(t));
                        projection.current.scale(s(t));
                        render(true);
                    };
                })
                .end()//.catch((err) => {
                //     // probably err due to clicking go back during this transition
                //     console.log("zoom in transition interrupted", err);
                // })
                .finally(() => {
                    zoomState.current = ZState.Zoomed;
                    render(false);
                });
            // forceUpdate();
            console.log("transition started");
        });

        render(false); //initial render of globe

        return () => {
            console.log(data, canvasRef);
        }
    }, [data, canvasRef]);

    //unzoom when the go back button is clicked
    const handleGoBack = useCallback(() => {
        setDisplayGoBack(false);
        zoomState.current = ZState.ZoomingOut;

        d3.transition()
            .duration(800)
            .tween("reset", () => {
                const s = d3.interpolate(projection.current.scale(), targetZoom); //back to original globe size

                return t => {
                    projection.current.scale(s(t));
                    render(true);
                };
            })
            .end().finally(() => {
                activeCountry.current = null;
                zoomState.current = ZState.NotZoomed;
            });
    }, [render, targetZoom]);

    return (
        <div style={{ width: "100%", height: "100vh", overflow: "hidden" }}>
            {displayGoBack && ( //renders button only when zoomed
                <button
                    //define appearance of go back button
                    // ref={goBackButtonRef}
                    onClick={handleGoBack}
                    style={{
                        position: "absolute",
                        top: "80px",
                        left: "50%",
                        transform: "translateX(-50%)",
                        // background: "white",
                        border: "2px solid black",
                        padding: "10px 20px",
                        cursor: "pointer",
                        zIndex: 10,
                        fontWeight: "bold",
                        borderRadius: "5px",
                    }}
                >
                    Go back to globe view
                </button>
            )}

            <canvas
                ref={canvasRef} //sets up surface to draw on
                width={dimensions.width}
                height={dimensions.height}
                style={{
                    // display: "block",
                    // position: "absolute",
                    top: 0,
                    left: 0,
                    cursor: zoomState.current === ZState.Zoomed ? "default" : isDragging ? "grab" : "default",
                }}
            />
        </div>
    );
};

export default Globe;
