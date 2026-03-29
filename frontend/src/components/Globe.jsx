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

    //creates the 3D globe
    const projection = useRef(
        d3
            .geoOrthographic()
            .scale(250) //globe size
            .translate([300, 300]), //canvas size is 600 x 600, this puts the globe at the center
    );

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
                borders50: topojson.mesh(world50, world50.objects.countries, (a, b) => a !== b),
                borders110: topojson.mesh(world110, world110.objects.countries, (a, b) => a !== b),

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

            //initializes canvas which allows for drawing borders
            const context = canvas.getContext("2d");

            //d3 function that converts coordinates to canvas shapes
            const path = d3.geoPath(projection.current, context);

            //when dragging use lower res data
            const land = lowRes ? data.land110 : data.land50;
            const borders = lowRes ? data.borders110 : data.borders50;

            //when changing frames, this erases previous frames to make way for new ones
            context.clearRect(0, 0, 600, 600);

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

            //checks if a country is selected, if it is highlight it
            if (targetCountry) {
                context.beginPath();
                path(targetCountry);
                context.fillStyle = "#f6ad55";
                context.fill();
                context.strokeStyle = "#fff";
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

            //draws borders between countries
            context.beginPath();
            path(borders);
            context.strokeStyle = "#fefefe";
            context.lineWidth = 0.9;
            context.stroke();
        },
        [data, activeCountry, projection.current],
    );

    useEffect(() => {
        if (!data || !canvasRef.current) return;

        const canvas = d3.select(canvasRef.current);

        //makes the user unable to move while in country view
        canvas.on(".drag", null);

        if (!isZoomed) {
            let v0, q0, r0;

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
        }

        //handles what happens when a user clicks on the globe
        canvas.on("click", event => {
            //if the user is already zoomed on a country, nothing happens
            if (isZoomed) return;

            //checks coordinate of user click
            const p = projection.current.invert(d3.pointer(event));
            //converts that coordinate to a country if the click is within a country
            const country = data.countries.find(f => d3.geoContains(f, p));

            if (country) {
                //if its in a country, choose that country
                setActiveCountry(country);
                //toggle being zoomed in
                setIsZoomed(true);

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
                const targetScale = Math.max(350, Math.min(2800, (600 / maxDim) * 35));

                d3.transition()
                    .duration(800)
                    .tween("zoom", () => {
                        //rotates globe to country while zooming
                        //zooms in over time
                        const r = d3.interpolate(projection.current.rotate(), [-centroid[0], -centroid[1]]);
                        const s = d3.interpolate(projection.current.scale(), targetScale);

                        return t => {
                            projection.current.rotate(r(t));
                            projection.current.scale(s(t));
                            render(country, true);
                        };
                    });
            }
        });

        //rerenders globe
        render();
    }, [data, isZoomed, activeCountry, render, projection.current]);

    //unzoom when the go back button is clicked
    const handleGoBack = () => {
        setIsZoomed(false);

        d3.transition()
            .duration(800)
            .tween("reset", () => {
                const s = d3.interpolate(projection.current.scale(), 250); //back to original globe size

                return t => {
                    projection.current.scale(s(t));
                    render(t === 1 ? null : activeCountry, true);

                    if (t === 1) setActiveCountry(null); //unselect country
                };
            });
    };

    return (
        <div style={{ position: "relative", width: "600px", margin: "0 auto" }}>
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
                width="600"
                height="600"
                style={{
                    cursor: isZoomed ? "default" : isDragging ? "grab" : "default",
                    display: "block",
                }}
            />
        </div>
    );
};

export default Globe;

//next tasks

// Make zooming in on the globe before selecting a country with mouse pad or scroll wheel functional
// Also could zoom with buttons if that is challenging

// Make zooming and rotating smoother

// Add pop up box for where news will show up

// Find how to link backend with this frontend

// Make stylistic changes Ari needs
//example options: change color of countries
//name of countries while hovering with mouse
//different background or fonts
//circular frame instead of square
//have outlines around countries even when no border is present

// Find how to actually get this visualization functional on a website, not just on localhost

//ptag space for sourcing individual articles, using publication and author
//make the mission always known
//use UTC, have update time frame in the transparency area
//we can have different news for each tone for each country

//make zoom in encapsulate whole thing, have words sit on top
