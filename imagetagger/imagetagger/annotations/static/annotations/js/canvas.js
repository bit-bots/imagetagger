const threshold = 7;      // Threshold to draw a new drawing vs move the old one (px)
const radius = 3;         // Radius of the handles
let mousex, mousey;       // Holding the mouse position relative to the canvas

/** The parent class for drawings */
class Drawing {
  /**
   * @param parent the parent Canvas object
   * @param points initial points
   * @param mutable whether the drawing may be changed
   */
  constructor(parent, points, id, mutable, color) {
    /* Set fields */
    this.pointCounter = Object.keys(points).length / 2;      // The number of points that are currently set
    this.id = id;
    this.name = "drawing" + id;
    this.parent = parent;
    this.color = color || globals.stdColor;

    /* Define layer */
    let l = {
      name: this.name,
      type: 'line',
      strokeWidth: mutable ? 3 : 2,
      strokeStyle: this.color,
    };
    $.extend(l, points);
    this.parent.addLayer(l);
    this.setMutable(mutable);
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
    this.parent.updateAnnotationFields(this.parent.getLayer(this.name));
  }
  setPoints(points) {
    this.parent.setLayer(this.name, points);
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
    if (l.handle && this.mutable) {
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
    this.parent.updateAnnotationFields(this.parent.getLayer(this.name));
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
  setMutable(mutable) {
    this.mutable = mutable;
    let l = this.parent.getLayer(this.name);
    if (mutable) {
      l["handle"] = {
        type: 'arc',
        fillStyle: globals.mutColor,
        strokeStyle: globals.mutColor,
        strokeWidth: 1,
        radius: radius,
        cursors: {
          mouseover: 'grab',
          mousedown: 'crosshair',
          mouseup: 'crosshair'
        }
      };
      l["strokeStyle"] = globals.mutColor;
      l["strokeWidth"] = 3;
    } else {
      l["handle"] = {};
      l["strokeStyle"] = this.color;
      l["strokeWidth"] = 2;
    }
    this.parent.setLayer(this.name, l);
  }

  /** Set the color of the annotation
   *
   * @param mutable boolean indicating if mutable color or not
   **/
  setColor(mutable) {
    let l = this.parent.getLayer(this.name);
    l["strokeStyle"] = mutable ? globals.mutColor : this.color;
    if (l["handle"] !== undefined) {
      l["handle"]["strokeStyle"] = mutable ? globals.mutColor : this.color;
      l["handle"]["fillStyle"] = mutable ? globals.mutColor : this.color;
      l["strokeWidth"] = mutable ? 3 : 2;
    }
    this.parent.setLayer(this.name, l);
  }

  /** Move the drawing
   *
   * @param x direction (in px) to the right
   * @param y direction (in px) to the bottom
   */
  move(x, y) {
    let l = this.parent.getLayer(this.name);
    for (let i = 1; i <= this.pointCounter; i++) { // TODO klären
      l["x" + i] = Math.min(Math.max(l["x" + i] + x, 0), globals.image.width());
      l["y" + i] = Math.min(Math.max(l["y" + i] + y, 0), globals.image.height());
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

class Point {
  constructor(parent, point, id, mutable, color) {
    /* Set fields */
    this.pointCounter = 1;      // The number of points that are currently set
    this.id = id;
    this.name = "drawing" + id;
    this.parent = parent;
    this.mutable = mutable;
    this.color = color || globals.stdColor;

    /* Define layer */
    let l = {
      name: this.name,
      type: 'ellipse',
      width: 6, height: 6,
      x: point.x1, y: point.y1,
      fillStyle: this.color,
    };
    this.parent.addLayer(l);
    this.parent.inline = false;
    this.parent.locked = false;
    this.parent.updateAnnotationFields(point);
  }
  /** Set the cursor to 'drag' or 'crosshair' in mouseover
   *
   * @param bool whether the dursor is in 'drag' style
   */
  setDragCursor(bool) {}
  setMutable(mutable) {}
  getPointTuples() {
    let l = this.parent.getLayer(this.name);
    return [[l.x, l.y]];
  }
  getPoints() {
    let l = this.parent.getLayer(this.name);
    return {x1: l.x, y1: l.y};
  }
  remove() {
    this.parent.removeLayer(this.name);
  }
}

class Line extends Drawing {
  constructor(parent, point, id, mutable, color) {
    super(parent, point, id, mutable, color);
    this.type = "line";
    this.color = color || globals.stdColor;
  }
  addPoint(x, y) {
    this.pointCounter++;
    if (this.pointCounter === 2) {
      this.setPoint(2, x, y);
      this.close();
    }
  }
}

class Multiline extends Drawing {
  constructor(parent, point, id, mutable, color) {
    super(parent, point, id, mutable, color);
    this.type = "multiline";
    this.color = color || globals.stdColor;
    this.parent.setLayer(this.name, {
      closed: false
    })
  }

  addPoint(x, y) {
      super.addPoint(x, y);
  }
  close() {
    this.deleteCurrentPoint();
    this.parent.inline = false;
    this.parent.locked = false;
    this.parent.setLayer(this.name, {
      closed: false
    });
    this.closed = true;
    this.setDragCursor(true);
    this.parent.updateAnnotationFields(this.parent.getLayer(this.name));
  }
}

class Polygon extends Drawing {
  /**
   * @param numberOfPoints The number of points the polygon will have
   */
  constructor(parent, points, id, mutable, numberOfPoints, color) {
    super(parent, points, id, mutable, color);
    this.type = "polygon";
    this.nop = numberOfPoints;
    this.color = color || globals.stdColor;
  }
  addPoint(x, y) {
    super.addPoint(x, y);
    this.parent.updateAnnotationFields(this.parent.getLayer(this.name));
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
  constructor(parent, point, id, mutable, color) {
    super(parent, point, id, mutable, color);
    this.type = "polygon";
    this.color = color || globals.stdColor;
  }
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
  constructor(HTMLCanvas, vector_type, node_count, annotationTypeId) {
    this.canvas = HTMLCanvas;
    this.width = this.canvas.width();
    this.height = this.canvas.height();
    this.offset = this.canvas.offset();
    this.inline = false;            // True if we are currently drawing a drawing
    this.locked = false;            // True if clicking should not create a new line
    this.vector_type = vector_type;
    this.node_count = node_count;
    this.currentDrawing = null;     // The drawing we are currently drawing
    this.drawings = [];             // Array holding all the drawings
    this.annotationTypeId = annotationTypeId;
    let self = this;
    // Update annotation fields to match vector type
    switch (vector_type) {
      case 2: // Point
        self.updateAnnotationFields({x1: 0, y1: 0});
        break;
      case 3: // Line, fallthrough
      case 4: // Multiline, fallthrough
      case 5: // Polygon
        self.updateAnnotationFields({x1: 0, x2: 0, y1: 0, y2: 0});
        break;
    }
  }

  mouseTooClose() {
    for (let drawing of this.drawings) {
      let points = drawing.getPointTuples();
      for (let point of points) {
        if (Math.abs(point[0] * globals.imageScaleWidth - globals.mouseDownX) < threshold && Math.abs(point[1] * globals.imageScaleHeight - globals.mouseDownY) < threshold) {
          return true;
        }
      }
    }
    return false;
  }

  /** ---- Layer operations ---- */

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
    this.drawings = this.drawings.filter(function (d) {
      return d.name !== name;
    });
  }

  /** ---- Public methods ---- **/

  clear() {
    for (let d of this.drawings) {
      d.remove();
    }
    switch (this.vector_type) {
      case 2: // Point
        this.updateAnnotationFields({x1: 0, y1: 0});
        break;
      case 3: // Line, fallthrough
      case 4: // Multiline, fallthrough
      case 5: // Polygon
        this.updateAnnotationFields({x1: 0, x2: 0, y1: 0, y2: 0});
        break;
    }
  }

  reset() {
    this.clear();
    $('body').off('click').off('mousemove').off('mousedown');
  }

  drawPoint(points, id, mutable, color) {
    color = color || globals.stdColor;
    this.currentDrawing = new Point(this, points, id, mutable, color);
    this.drawings.push(this.currentDrawing);
  }

  drawLine(points, id, mutable, color) {
    color = color || globals.stdColor;
    this.currentDrawing = new Line(this, points, id, mutable, color);
    this.drawings.push(this.currentDrawing);
  }

  drawMultiline(points, id, mutable, color) {
    color = color || globals.stdColor;
    this.currentDrawing = new Multiline(this, points, id, mutable, color);
    this.drawings.push(this.currentDrawing);
  }

  drawPolygon(points, id, mutable, numberOfPoints, closed, color) {
    color = color || globals.stdColor;
    this.currentDrawing = new Polygon(this, points, id, mutable, numberOfPoints, color);
    if (closed) {
      this.currentDrawing.close();
    }
    this.drawings.push(this.currentDrawing);
  }

  drawArbitraryPolygon(points, id, mutable, closed, color) {
    color = color || globals.stdColor;
    this.currentDrawing = new ArbitraryPolygon(this, points, id, mutable, color);
    if (closed) {
      this.currentDrawing.close();
    }
    this.drawings.push(this.currentDrawing);
  }

  drawExistingAnnotations(annotations, color) {
    this.clear();
    color = color || globals.stdColor;
    let colors = [];
    if (color.constructor === Array) {
      colors = color;
      if (color.length != annotations.length) {
        console.log('wrong number of colors');
        return;
      }
    } else {
      for (let i = 0; i < annotations.length; i++) {
        colors.push(color);
      }
    }
    if (!globals.drawAnnotations) {
      return;
    }
    for (let i in annotations) {
      let annotation = annotations[i];
      let color = colors[i];
      console.log(annotation);
      console.log(color);
      if (annotation.annotation_type.id !== this.annotationTypeId) {
        continue;
      }
      if (annotation.vector === null) {
        continue;
      }
      let vector = {};
      for (let key in annotation.vector) {
        if (key[0] === "y") {
          vector[key] = annotation.vector[key] / globals.imageScaleHeight;
        } else {
          vector[key] = annotation.vector[key] / globals.imageScaleWidth;
        }
      }
      switch (annotation.annotation_type.vector_type) {
        case 1: // Ball
          console.log("Bounding boxes should be used for this");
          break;
        case 2: // Points
          this.drawPoint(vector, annotation.id, false, color);
          break;
        case 3: // Lines
          this.drawLine(vector, annotation.id, false, color);
          break;
        case 4: // Multilines
          this.drawMultiline(vector, annotation.id, false, color);
          break;
        case 5: // Polygons
          if (annotation.annotation_type.node_count === 0) {
            this.drawArbitraryPolygon(vector, annotation.id, false, true, color);
          } else {
            this.drawPolygon(vector, annotation.id, false, annotation.annotation_type.node_count, true, color);
          }
          break;
        default:
          console.log("Unknown vector type: " + annotation.annotation_type.vector_type);
      }
    }
    this.currentDrawing = undefined;
  }

  updateAnnotationFields(drawing) {
    let not_in_image_cb = $('#not_in_image');
    if (not_in_image_cb.prop('checked')) {
      $('#not_in_image').prop('checked', false).change();
    }
    if (drawing.type === "ellipse") {
      drawing.x1 = drawing.x;
      drawing.y1 = drawing.y;
    }
    // Add missing fields
    let i = 1;
    for (; drawing.hasOwnProperty("x" + i); i++) {
      if (!$('#x' + i + 'Field').length) {
        $('#coordinate_table').append(this.getTag("x" + i)).append(this.getTag("y" + i));
      }
    }
    // Remove unnecessary fields
    for (; $('#x' + i + 'Field').length; i++) {
      $('#x' + i + 'Box').remove();
      $('#y' + i + 'Box').remove();
    }
    for (let j = 1; drawing.hasOwnProperty("x" + j); j++) {
      $('#x' + j + 'Field').val(parseInt(Math.max(Math.min(drawing["x" + j], globals.image.width()), 0) * globals.imageScaleWidth));
      $('#y' + j + 'Field').val(parseInt(Math.max(Math.min(drawing["y" + j], globals.image.height()), 0) * globals.imageScaleHeight));
    }
  }

  getTag(field) {
    return '<div id="' + field + 'Box"><div class="col-xs-2" style="max-width: 3em">' +
              '<label for="' + field + 'Field">' + field + '</label>' +
              '</div><div class="col-xs-10">' +
              '<input id="' + field + 'Field" class="Coordinates annotation_value form-control"' +
              'type="text" name="' + field + 'Field" value="0" min="0" disabled>' +
              '</div><div class="col-xs-12"></div></div>';
  }

  getDrawingById(id) {
    for (let drawing of this.drawings) {
      if (drawing.id === id) {
        return drawing;
      }
    }
  }

  closeDrawing() {
    if (this.currentDrawing && this.annotationTypeId === 4 && !this.currentDrawing.closed) {
      this.currentDrawing.close();
    }
  }

  resetSelection() {
    $('.annotation_value').val(0);
    // Make every drawing immutable
    for (let drawing of this.drawings) {
      drawing.setMutable(false);
    }
    if (this.old && this.currentDrawing) {
        this.currentDrawing.setPoints(this.old);
        this.old = undefined;
      } else if (this.currentDrawing) {
        this.currentDrawing.remove();
      }
      this.currentDrawing = undefined;
  }

  cancelSelection() {
    this.resetSelection(true)
  }

  initSelection() {
    this.initialized = true;
  }

  /**
   * Restore the selection.
   */
  restoreSelection(reset) {
    if (!$('#keep_selection').prop('checked')) {
      return;
    }
    if (globals.restoreSelection !== undefined) {
      if (globals.restoreSelection === null) {
        $('#not_in_image').prop('checked', true);
        $('#coordinate_table').hide();
        let concealed = $('#concealed');
        let concealedP = $('#concealed_p');
        let blurred = $('#blurred');
        let blurredP = $('#blurred_p');
        concealedP.hide();
        concealed.prop('checked', false);
        concealed.prop('disabled', true);
        blurredP.hide();
        blurred.prop('checked', false);
        blurred.prop('disabled', true);
      } else if (globals.restoreSelectionVectorType === 4) {
        // this is not implemented for multilines, so just do nothing
        this.old = undefined;
      } else {
        let vector = {};
        for (let key in globals.restoreSelection) {
          if (key[0] === "y") {
            vector[key] = globals.restoreSelection[key] / globals.imageScaleHeight;
          } else {
            vector[key] = globals.restoreSelection[key] / globals.imageScaleWidth;
          }
        }
        this.updateAnnotationFields(globals.restoreSelection);
        switch(globals.restoreSelectionVectorType) {
          case 2: this.drawPoint(vector, 0, true); break;
          case 3: this.drawLine(vector, 0, true); break;
          case 5: if (globals.restoreSelectionNodeCount === 0) {
            this.drawArbitraryPolygon(vector, 0, true, true);
          } else {
            this.drawPolygon(vector, 0, true, globals.restoreSelectionNodeCount, true);
          }
        }
        this.reloadSelection(0);
        this.old = undefined;
      }
    }
    if (reset !== false) {
      globals.restoreSelection = undefined;
      globals.restoreSelectionNodeCount = 0;
      globals.restoreSelectionVectorType = 1;
    }
  }

  setHighlightColor(id) {
    let d = this.getDrawingById(id);
    d.setColor(true);
  }

  unsetHighlightColor(id) {
    let d = this.getDrawingById(id);
    d.setColor(false);
  }

  reloadSelection(annotation_id) {
    this.currentDrawing = this.getDrawingById(annotation_id);
    this.currentDrawing.setMutable(true);
    this.old = this.currentDrawing.getPoints();
    this.updateAnnotationFields(this.getLayer(this.currentDrawing.name));
  }

  moveSelectionLeft() {
    this.currentDrawing.move(-globals.moveSelectionStepSize, 0);
    this.updateAnnotationFields(this.getLayer(this.currentDrawing.name));
  }
  moveSelectionRight() {
    this.currentDrawing.move(globals.moveSelectionStepSize, 0);
    this.updateAnnotationFields(this.getLayer(this.currentDrawing.name));
  }
  moveSelectionUp() {
    this.currentDrawing.move(0, -globals.moveSelectionStepSize);
    this.updateAnnotationFields(this.getLayer(this.currentDrawing.name));
  }
  moveSelectionDown() {
    this.currentDrawing.move(0, globals.moveSelectionStepSize);
    this.updateAnnotationFields(this.getLayer(this.currentDrawing.name));
  }
  decreaseSelectionSizeFromRight() {}
  decreaseSelectionSizeFromTop() {}
  increaseSelectionSizeRight() {}
  increaseSelectionSizeUp() {}

  handleMouseClick(event) {
    let position = globals.image.offset();
    if (!(event.pageX > position.left && event.pageX < position.left + globals.image.width() &&
      event.pageY > position.top && event.pageY < position.top + globals.image.height()) &&
      this.annotationTypeId === 4 && this.currentDrawing) {
      this.currentDrawing.close();
    }
  }

  handleMouseDown() {
    // Check if we are close enough to move the point, not draw a new drawing
    // we use the variable locked which is checked when we can create a new line
    if (this.mouseTooClose()) {
      this.locked = true;
    }
  }

  handleMouseUp() {
    if (this.inline && this.currentDrawing) {
      // We are currently drawing a drawing
      // and we clicked inside of the canvas:
      // add a point
      this.currentDrawing.addPoint(globals.mouseUpX, globals.mouseUpY);
    } else if (this.locked) {
      // we do not create a drawing because we are
      // only moving an existing one
      this.locked = false;
    } else {
      // We clicked and are inside the canvas:
      // start drawing a new one
      if (this.currentDrawing) {
        this.currentDrawing.remove();
      }
      this.inline = true;
      switch (this.vector_type) {
        case 2: // Point
          this.drawPoint({x1: globals.mouseUpX, y1: globals.mouseUpY}, 0, true);
          break;
        case 3: // Line
          this.drawLine({x1: globals.mouseUpX, y1: globals.mouseUpY}, 0, true);
          break;
        case 4: // Multiline
          this.drawMultiline({x1: globals.mouseUpX, y1: globals.mouseUpY}, 0, true);
          break;
        case 5: // Polygon
          if (this.node_count === 0) {
            this.drawArbitraryPolygon({x1: globals.mouseUpX, y1: globals.mouseUpY}, 0, true, false);
          } else {
            this.drawPolygon({x1: globals.mouseUpX, y1: globals.mouseUpY}, 0, true, this.node_count, false);
          }
          break;
        default:
          console.log("No appropriate drawing found for vector type " + this.vector_type);
          this.inline = false;
      }
      this.currentDrawing.setDragCursor(false);
    }
  }

  handleMousemove(event) {
    mousex = event.pageX - globals.image.offset().left;
    mousey = event.pageY - globals.image.offset().top;
    if (this.inline && this.currentDrawing) {
      this.currentDrawing.setCurrentPoint(mousex, mousey);
    }
    if (this.currentDrawing) {
      this.updateAnnotationFields(this.getLayer(this.currentDrawing.name));
    }
  }
}
