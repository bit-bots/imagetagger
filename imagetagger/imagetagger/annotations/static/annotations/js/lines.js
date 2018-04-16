'use-strict';

const threshold = 7;      // Threshold to draw a new drawing vs move the old one (px)
const radius = 3;         // Radius of the handles
const color = '#C00';     // The color of drawings and handles
let mousex, mousey;       // Holding the mouse position relative to the canvas


/** The parent class for drawings */
class Drawing {
    /**
     * @param parent the parent Canvas object
     * @param name the name of the drawing, used for reference
     * @param points initial points
     * @param mutable whether the drawing may be changed
     */
    constructor(parent, name, points, mutable) {
        /* Set fields */
        this.pointCounter = points.length / 2;      // The number of points that are currently set
        this.name = name;
        this.parent = parent;

        /* Define layer */
        let l = {
            name: name,
            type: 'line',
            strokeWidth: 2,
            strokeStyle: color,
        };
        for (let i = 1; i <= this.pointCounter; i++) {
            l["x" + i] = points[2 * i - 2];
            l["y" + i] = points[2 * i - 1];
        }
        if (mutable) {
            l["handle"] = {
                type: 'arc',
                fillStyle: color,
                strokeStyle: color,
                strokeWidth: 1,
                radius: radius,
                cursors: {
                    mouseover: 'grab',
                    mousedown: 'crosshair',
                    mouseup: 'crosshair'
                }
            };
        }
        this.parent.addLayer(l);
    }
    /** Used so that the line can follow the mouse */
    setCurrentPoint(x, y) {
        this.setPoint(this.pointCounter + 1, x, y);
    }

    /** Set a specific point to specified coordinates */
    setPoint(number, x, y) {
        let l = {};
        l["x" + number] = x;
        l["y" + number] = y;
        this.parent.setLayer(this.name, l);
    }
    /** Deletes the current point */
    deleteCurrentPoint() {
        this.pointCounter++;
        this.deletePoint(this.pointCounter);
    }

    /** Set the cursor to 'drag' or 'crosshair' in mouseover
     *
     * @param bool whether the dursor is in 'drag' style
     */
    setDragCursor(bool) {
        let l = this.parent.getLayer(this.name);
        if (l.handle) {
            l.handle.cursors.mouseover = bool ? 'grab' : 'crosshair';
            this.parent.setLayer(this.name, l);
        }
    }
    /** Finish the current drawing */
    close() {
        this.parent.inline = false;
        this.parent.locked = false;
        this.parent.setLayer(this.name, {
            closed: true
        });
        this.setDragCursor(true);
    }
    /** Return the points of the drawing as a JS object
     * with the properties x1, y1, x2, y2, ...
     */
    getPoints() {
        let points = {};
        let l = this.parent.getLayer(this.name);
        for (let i = 1; i <= this.pointCounter; i++) {
            points["x" + i] = l["x" + i];
            points["y" + i] = l["y" + i];
        }
        return points;
    }
    /** Return the points of the drawing as an array
     * containing an array of length two for each point
     * e.g. [[12, 41], [124, 35], ...]
     */
    getPointTuples() {
        let points = [];
        let l = this.parent.getLayer(this.name);
        for (let i = 1; i <= this.pointCounter; i++) {
            points.push([l["x" + i], l["y" + i]]);
        }
        return points;
    }

    /** ---- Public methods ---- **/

    /** Remove the drawing **/
    remove() {
        this.parent.removeLayer(this.name);
    }
    /** Move the drawing
     *
     * @param x direction (in px) to the right
     * @param y direction (in px) to the bottom
     */
    move(x, y) {
        let l = this.parent.getLayer(this.name);
        for (let i = 1; i <= this.pointCounter; i++) {
            l["x" + i] += x;
            l["y" + i] += y;
        }
        this.parent.setLayer(this.name, l);
    }
    addPoint(x, y) {
        this.setCurrentPoint(x, y);
        this.pointCounter++;
    }
    /**
     * @param number number of the point, starting at 1
     */
    deletePoint(number) {
        let l = this.parent.getLayer(this.name);
        for (let i = number; i < this.pointCounter; i++) {
            l["x" + i] = l["x" + (i + 1)];
            l["y" + i] = l["y" + (i + 1)];
        }
        delete l["x" + this.pointCounter];
        delete l["y" + this.pointCounter];
        this.pointCounter--;
        if (this.pointCounter === 0) {
            this.remove();
        } else {
            this.parent.setLayer(this.name, l);
        }
    }
}

class Line extends Drawing {
    addPoint(x, y) {
        this.pointCounter++;
        if (this.pointCounter === 2) {
            this.setPoint(2, x, y);
            this.close();
        }
    }
}

class Polygon extends Drawing {
    /**
     * @param numberOfPoints The number of points the polygon will have
     */
    constructor(parent, name, points, mutable, numberOfPoints) {
        super(parent, name, points, mutable);
        this.nop = numberOfPoints;
    }
    addPoint(x, y) {
        super.addPoint(x, y);
        if (this.pointCounter >= this.nop) {
            this.close();
        }
    }
}

/** Polygons with an arbitrary number of points
 *
 * Clicking on the first point will finish the drawing.
 */
class ArbitraryPolygon extends Drawing {
    addPoint(x, y) {
        let firstPoint = this.getPointTuples()[0];
        if (Math.abs(firstPoint[0] - mousex) < threshold &&
            Math.abs(firstPoint[1] - mousey) < threshold) {
            this.deleteCurrentPoint();
            this.close();
        } else {
            super.addPoint(x, y);
        }
    }
}


class Canvas {
    constructor(HTMLCanvas, image, mutable) {
        this.canvas = HTMLCanvas;
        this.width = this.canvas.width();
        this.height = this.canvas.height();
        this.offset = this.canvas.offset();
        this.inline = false;            // True if we are currently drawing a drawing
        this.locked = false;            // True if clicking should not create a new line
        this.mutable = mutable;         // Whether we can draw on the canvas with the mouse
        this.currentDrawing = null;     // The drawing we are currently drawing
        this.drawingCounter = 0;        // Number of drawings, only used for naming purposes
        this.drawings = [];             // Array holding all the drawings
        let self = this;
        $('body').mousemove(function (event) {
            mousex = event.pageX - self.offset.left;
            mousey = event.pageY - self.offset.top;
            if (self.inline && self.currentDrawing) {
                self.currentDrawing.setCurrentPoint(mousex, mousey);
            }
        }).click(function (event) {
            mousex = event.pageX - self.offset.left;
            mousey = event.pageY - self.offset.top;
            if (self.inline && self.currentDrawing) {
                if (mousex <= self.width && mousex >= 0 &&
                    mousey <= self.height && mousey >= 0) {
                    // We are currently drawing a drawing
                    // and we clicked inside of the canvas:
                    // add a point
                    self.currentDrawing.addPoint(mousex, mousey);
                }
            } else if (self.locked) {
                // we do not create a drawing because we are
                // only moving an existing one
                self.locked = false;
            } else if (self.mutable) {
                if (mousex <= self.width && mousex >= 0 &&
                    mousey <= self.height && mousey >= 0) {
                    // We clicked and are inside the canvas:
                    // start drawing a new one
                    self.drawLineMouse("drawing" + self.drawingCounter++);
                }
            }
        }).mousedown(function () {
            // Check if we are close enough to move the point, not draw a new drawing
            // we use the variable locked which is checked when we can create a new line
            if(self.mouseTooClose()) {
                self.locked = true;
            }
        });
        this.addLayer({
            name: 'background',
            type: 'image',
            source: image,
            x: 0, y: 0,
            width: this.width, height: this.height,
            fromCenter: false
        });
    }
    mouseTooClose() {
        for (let drawing of this.drawings) {
            let points = drawing.getPointTuples();
            for (let point of points) {
                if (Math.abs(point[0] - mousex) < threshold && Math.abs(point[1] - mousey) < threshold) {
                    return true;
                }
            }
        }
        return false;
    }
    addLayer(l) {
        this.canvas.addLayer(l).drawLayers();
    }
    setLayer(name, l) {
        this.canvas.setLayer(name, l).drawLayers();
    }
    getLayer(name) {
        return this.canvas.getLayer(name);
    }
    removeLayer(name) {
        this.canvas.removeLayer(name).drawLayers();
        this.drawings = this.drawings.filter(function(d) {
            return d.name !== name;
        });
    }
    drawLineMouse(name) {
        this.inline = true;
        this.drawLine(name, [mousex, mousey], true);
        this.currentDrawing.setDragCursor(false);
    }
    drawPolygonMouse(name, numberOfPoints) {
        this.inline = true;
        this.drawPolygon(name, [mousex, mousey], true, numberOfPoints, false);
        this.currentDrawing.setDragCursor(false);
    }
    drawArbitraryPolygonMouse(name) {
        this.inline = true;
        this.drawArbitraryPolygon(name, [mousex, mousey], true, false);
        this.currentDrawing.setDragCursor(false);
    }

    /** ---- Public methods ---- **/

    setImage(image) {
        this.setLayer('background', {
            source: image,
        });
    }
    clear() {
        for (let d of this.drawings) {
            d.remove();
        }
    }
    drawLine(name, points, mutable) {
        this.currentDrawing = new Line(this, name, points, mutable);
        this.drawings.push(this.currentDrawing);
    }
    drawPolygon(name, points, mutable, numberOfPoints, closed) {
        this.currentDrawing = new Polygon(this, name, points, mutable, numberOfPoints);
        if (closed) {
            this.currentDrawing.close();
        }
        this.drawings.push(this.currentDrawing);
    }
    drawArbitraryPolygon(name, points, mutable, closed) {
        this.currentDrawing = new ArbitraryPolygon(this, name, points, mutable);
        if (closed) {
            this.currentDrawing.close();
        }
        this.drawings.push(this.currentDrawing);
    }

    /** Display a set of given lines/polygons.
     * points should be an array containing an
     * array for each point of the line/polygon **/

    loadLines(points) {
        for (let point of points) {
            this.drawLine("line" + this.drawingCounter++, point, this.mutable);
        }
    }
    loadPolygons(points) {
        for (let point of points) {
            this.drawPolygon("line" + this.drawingCounter++, point, this.mutable, point.length / 2, true);
        }
    }
    loadArbitraryPolygons(points) {
        this.loadPolygons(points);
    }

    /** Exports the drawings as JSON **/
    exportDrawings() {
        let points = [];
        for (let drawing of this.drawings) {
            points.push(drawing.getPoints());
        }
        return JSON.stringify(points);
    }
}

let c = new Canvas($('canvas'), "example.png", true);
