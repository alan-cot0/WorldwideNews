import React, { useEffect, useRef, useState, useCallback } from "react";
import * as d3 from "d3";

// This is the dataset that holds the country boundaries and globe data
import * as topojson from "topojson-client";

// Used for dragging and calculating appearance of 3D globe
import versor from "versor";

const Globe = () => {
    const canvasRef = useRef(null);

    //data is used to contain land shapes, borders, and country lists
    const [data, setData] = useState(null);

    //stores current selected country by user
    const [activeCountry, setActiveCountry] = useState(null);

    //if true user is currently zoomed in on a country where the news will pop up
    const [isZoomed, setIsZoomed] = useState(false);

    //if true user is currently dragging the globe
    const [isDragging, setIsDragging] = useState(false);

    //if true user is zooming in either by clicking on the country or using the zoom feature
    const [isZooming, setIsZooming] = useState(false);

    //set dimensions to fill screen
    const [dimensions, setDimensions] = useState({ 
        width: window.innerWidth, 
        height: window.innerHeight 
    });

    //creates the 3D globe
    const projection = useRef(
        d3.geoOrthographic().scale(350) //globe size
    );

    //checking which country mouse is hovering over
    const [hoveredCountry, setHoveredCountry] = useState(null);

    //added to keep resized globe
    useEffect(() => {
        const handleResize = () => {
            const w = window.innerWidth;
            const h = window.innerHeight;
            setDimensions({ width: w, height: h });
            projection.current.translate([w / 2, h / 2]);
            render();
        };
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [data, activeCountry]);

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

    //render draws the globe, gets called when view changes
    const render = useCallback(
        (targetCountry = activeCountry, lowRes = false) => {
            const canvas = canvasRef.current;
            if (!canvas || !data) return;


            const w = canvas.width;
            const h = canvas.height;



            //initializes canvas which allows for drawing borders
            const context = canvas.getContext("2d");

            projection.current.translate([w / 2, h / 2]);

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

            //checks if a country is selected, if it is highlight it
            if (targetCountry) {
                context.beginPath();
                path(targetCountry);
                context.fillStyle = "#f6ad55";
                context.fill();
                context.strokeStyle = "#ffffff";
                context.lineWidth = 1;
                context.stroke();

                //adds name of country when zoomed in
                if (projection.current.scale() > 300 && !lowRes) {
                    const centroid = projection.current(d3.geoCentroid(targetCountry));
                    context.fillStyle = "#000000";
                    context.font = "bold 20px Arial";
                    context.textAlign = "center";
                    context.shadowBlur = 4;
                    context.shadowColor = "white";
                    context.fillText(targetCountry.properties.name, centroid[0], centroid[1] - 20);
                    context.shadowBlur = 0;
                }
            }
            else {
                //highlight/distinguish hovered country
                if (hoveredCountry && hoveredCountry !== activeCountry) {
                    context.beginPath();
                    path(hoveredCountry);
                    context.fillStyle = "rgba(255, 255, 255, 0.3)"; // Subtle white overlay
                    context.fill();
                }
                
                //add hovered countries name
                const countryToLabel = hoveredCountry;
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




        },
        [data, activeCountry, projection.current, dimensions, hoveredCountry],
    );

    useEffect(() => {
        if (!data || !canvasRef.current) return;

        const canvas = d3.select(canvasRef.current);

        //makes the user unable to move while in country view
        canvas.on(".drag", null);
        canvas.on(".zoom", null);
    


        if (!isZoomed) {
            let v0, q0, r0;

            //zoom functionality
            const initialScale = 350;
            const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .filter(event => {
                return event.type === 'wheel' || (event.touches && event.touches.length > 1);
            })
            .on("zoom", (event) => {
                projection.current.scale(initialScale * event.transform.k);
                render(activeCountry, true);
            })
            .on("end", () => {
                render(activeCountry, false);
            });

            canvas.call(zoom)
            .on("mousedown.zoom", null)
            .on("touchstart.zoom", null);


            //d3.drag handles the dragging motion
            const drag = d3
                .drag()
                .on("start", event => {
                    //the globe is being dragged
                    setIsDragging(true);

                    v0 = versor.cartesian(projection.current.invert([event.x, event.y])); //stores starting vector
                    q0 = versor((r0 = projection.current.rotate())); //updates globe based on user input
                })
                .on("drag", event => {
                    const v1 = versor.cartesian(projection.current.rotate(r0).invert([event.x, event.y]));
                    projection.current.rotate(versor.rotation(versor.multiply(q0, versor.delta(v0, v1))));

                    //low resolution during drag
                    render(activeCountry, true);
                })
                .on("end", () => {
                    setIsDragging(false); //globe no longer being dragged
                    render(activeCountry, false);
                });

            canvas.call(drag);


            //track mouse hovering
            canvas.on("mousemove", (event) => {
            
            const [mouseX, mouseY] = d3.pointer(event);
            const coords = projection.current.invert([mouseX, mouseY]);
            const country = coords && data.countries.find(f => d3.geoContains(f, coords));
            if (country !== hoveredCountry) {
                setHoveredCountry(country);
            }
            });
            canvas.on("mouseleave", () => setHoveredCountry(null));
        }

        //handles what happens when a user clicks on the globe
        
        canvas.on("click", event => {
            //if the user is already zoomed on a country, nothing happens
            if (isZoomed) return;

            //checks coordinate of user click
            const p = projection.current.invert(d3.pointer(event));
            //converts that coordinate to a country if the click is within a country
            const country = data.countries.find(f => d3.geoContains(f, p));

            /*if (hoveredCountry != null) {
                context.beginPath();
                path(hoveredCountry);
                context.fillStyle = "#38a169";
                context.fill();
            }*/

            if (country) {
                //stop name hovering
                setHoveredCountry(null);
                //canvas.on("mousemove", null);
                //canvas.on("mouseleave", null);

                //if its in a country, choose that country
                setActiveCountry(country);
                //toggle being zoomed in
                setIsZoomed(true);

                setIsZooming(true);

                //render(undefined, true);

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

                //sets zoom in limit
                const targetScale = Math.max(350, Math.min(3000, (dimensions.width / maxDim) * 23));

                d3.transition()
                    .duration(1200)
                    .tween("zoom", () => {
                        //rotates globe to country while zooming
                        //zooms in over time
                        const r = d3.interpolate(projection.current.rotate(), [-centroid[0], -centroid[1]]);
                        const s = d3.interpolate(projection.current.scale(), targetScale);

                        return t => {
                            projection.current.rotate(r(t));
                            projection.current.scale(s(t));
                            render(country);
                        };
                    });

                setIsZooming(false);
                render(undefined, false)
            }
        });

        //rerenders globe
        render();
    }, [data, isZoomed, activeCountry, render, projection.current, dimensions]);

    //unzoom when the go back button is clicked
    const handleGoBack = () => {
        setIsZoomed(false);

        render(undefined, false)

        d3.transition()
            .duration(800)
            .tween("reset", () => {
                const s = d3.interpolate(projection.current.scale(), 250); //back to original globe size

                return t => {
                    projection.current.scale(s(t));
                    render(t === 1 ? null : activeCountry);

                    if (t === 1) setActiveCountry(null); //unselect country
                };
            });
        render(undefined, true)
    };

    return (
        <div style={{ width: "100vw", height: "100vh", overflow: "hidden" }}>
            {isZoomed && ( //renders button only when zoomed
                <button
                    //define appearance of go back button
                    onClick={handleGoBack}
                    style={{
                        position: "absolute",
                        top: "20px",
                        left: "50%",
                        transform: "translateX(-50%)",
                        background: "white",
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
                    display: "block",
                    position: "absolute",
                    top: 0,
                    left: 0,
                    cursor: isZoomed ? "default" : isDragging ? "grab" : "default",
                }}
            />
        </div>
    );
};

export default Globe;

//next tasks

// Add pop up box for where news will show up

// Find how to link backend with this frontend

//ptag space for sourcing individual articles, using publication and author
//make the mission always known
//use UTC, have update time frame in the transparency area
//we can have different news for each tone for each country

//make zoom in encapsulate whole thing, have words sit on top
