// JS file for bounding box internals

class BoundingBoxes {
  constructor(annotationTypeId, noSelection) {
    this.initialized = false;
    this.selection = undefined;
    this.vector_type = 1;
    if (globals.image === '') {
      globals.image = $('#image');
    }
    this.annotationTypeId = annotationTypeId;
    if (!noSelection) {
      this.initSelection();
    }
  }

  drawExistingAnnotations(annotations, color) {
    this.clear();
    calculateImageScale();
    color = color || globals.stdColor;

    if (annotations.length === 0 || !globals.drawAnnotations) {
      return;
    }

    // clear all boxes
    let boundingBoxes = document.getElementById('boundingBoxes');

    for (let a in annotations) {

      let annotation = annotations[a];
      if (annotation.annotation_type.id !== this.annotationTypeId) {
        continue;
      }
      if (annotation.vector === null) {
        continue;
      }

      let boundingBox = document.createElement('div');
      boundingBox.setAttribute('class', 'boundingBox');
      boundingBox.setAttribute('id', 'boundingBox' + annotation.id);
      $(boundingBox).data('annotationid', annotation.id);
      $(boundingBox).css({
        'top': annotation.vector.y1 / globals.imageScaleHeight,
        'left': annotation.vector.x1 / globals.imageScaleWidth + parseFloat($('img#image').parent().css('padding-left')),
        'width': (annotation.vector.x2 - annotation.vector.x1) / globals.imageScaleWidth,
        'height': (annotation.vector.y2 - annotation.vector.y1) / globals.imageScaleHeight,
        'border': '2px solid ' + color
      });

      boundingBoxes.appendChild(boundingBox);
    }
  }

  setHighlightColor(id) {
    let highlightBox;
    for (let box of $('.boundingBox')) {
      if ($(box).data('annotationid') === id) {
        highlightBox = box;
        break;
      }
    }
    if (highlightBox) {
      $(highlightBox).css({
        'border': '3px solid ' + globals.mutColor
      });
    }
  }

  unsetHighlightColor(id) {
    let highlightBox;
    for (let box of $('.boundingBox')) {
      if ($(box).data('annotationid') === id) {
        highlightBox = box;
        break;
      }
    }
    if (highlightBox) {
      $(highlightBox).css({
        'border': '2px solid ' + globals.stdColor
      });
    }
  }

  clear() {
    let boundingBoxes = document.getElementById('boundingBoxes');

    while (boundingBoxes.firstChild) {
      boundingBoxes.removeChild(boundingBoxes.firstChild);
    }
  }

  /**
   * Initialize the selection.
   */
  initSelection() {
    this.initialized = true;

    this.selection = globals.image.imgAreaSelect({
      instance: true,
      show: true,
      minHeight: 2,
      minWidth: 2,
      onSelectChange: this.updateAnnotationFields,
      resizeMargin: 3
    });
    this.selection.cancelSelection();
  }

  /**
   * Reload the selection.
   */
  reloadSelection(annotationId, annotationData) {
    this.setHighlightColor(annotationId);
    this.selection = globals.image.imgAreaSelect({
      instance: true,
      show: true
    });
    if (!annotationData) {
      annotationData = {
        x1: parseInt($('#x1Field').val()),
        y1: parseInt($('#y1Field').val()),
        x2: parseInt($('#x2Field').val()),
        y2: parseInt($('#y2Field').val())
      };
    }
    let scaled_selection = {
      x1: annotationData.x1 / globals.imageScaleWidth,
      y1: annotationData.y1 / globals.imageScaleHeight,
      x2: annotationData.x2 / globals.imageScaleWidth,
      y2: annotationData.y2 / globals.imageScaleHeight
    };
    this.updateAnnotationFields(null, scaled_selection);
    this.selection.setSelection(
      scaled_selection.x1,
      scaled_selection.y1,
      scaled_selection.x2,
      scaled_selection.y2
    );
    this.selection.update();
  }

  /**
   * Delete current selection.
   */
  resetSelection() {
    this.unsetHighlightColor(globals.editedAnnotationsId);
    $('.annotation_value').val(0);

    if (this.selection !== undefined) {
      this.selection.cancelSelection();
    }

    globals.editedAnnotationsId = undefined;
    $('.annotation').removeClass('alert-info');
    globals.editActiveContainer.addClass('hidden');
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
      } else {
        $('#x1Field').val(globals.restoreSelection.x1);
        $('#x2Field').val(globals.restoreSelection.x2);
        $('#y1Field').val(globals.restoreSelection.y1);
        $('#y2Field').val(globals.restoreSelection.y2);
        this.reloadSelection(0, globals.restoreSelection);
      }
    }
    if (reset !== false) {
      globals.restoreSelection = undefined;
    }
  }

  moveSelectionUp() {
    // calculate value +/- stepsize (times stepsize to account for differing image sizes)
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleHeight)));
    let newValueY2 = Math.round(parseInt($('#y2Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleHeight)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0) {
      newValueY1 = 0;
      newValueY2 = $('#y2Field').val();
    }
    if (newValueY2 > Math.round(globals.image.height() * globals.imageScaleHeight)) {
      newValueY2 = Math.ceil(globals.image.height() * globals.imageScaleHeight);
      newValueY1 = $('#y1Field').val();
    }
    // update values
    $('#y1Field').val(newValueY1);
    $('#y2Field').val(newValueY2);
    this.reloadSelection();
  }

  moveSelectionDown() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleHeight)));
    let newValueY2 = Math.round(parseInt($('#y2Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleHeight)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0) {
      newValueY1 = 0;
      newValueY2 = $('#y2Field').val();
    }
    if (newValueY2 > Math.round(globals.image.height() * globals.imageScaleHeight)) {
      newValueY2 = Math.ceil(globals.image.height() * globals.imageScaleHeight);
      newValueY1 = $('#y1Field').val();
    }
    // update values
    $('#y1Field').val(newValueY1);
    $('#y2Field').val(newValueY2);
    this.reloadSelection();
  }

  moveSelectionRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX1 = Math.round(parseInt($('#x1Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleWidth)));
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleWidth)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0) {
      newValueX1 = 0;
      newValueX2 = $('#x2Field').val();
    }
    if (newValueX2 > Math.round(globals.image.width() * globals.imageScaleWidth)) {
      newValueX2 = Math.ceil(globals.image.width() * globals.imageScaleWidth);
      newValueX1 = $('#x1Field').val();
    }
    // update values
    $('#x1Field').val(newValueX1);
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  moveSelectionLeft() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX1 = Math.round(parseInt($('#x1Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleWidth)));
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleWidth)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0) {
      newValueX1 = 0;
      newValueX2 = $('#x2Field').val();
    }
    if (newValueX2 > Math.round(globals.image.width() * globals.imageScaleWidth)) {
      newValueX2 = Math.ceil(globals.image.width() * globals.imageScaleWidth);
      newValueX1 = $('#x1Field').val();
    }
    // update values
    $('#x1Field').val(newValueX1);
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  increaseSelectionSizeUp() {
    // calculate value +/- stepsize (times stepsize to account for differing image sizes)
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleHeight)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0) {
      newValueY1 = 0;
    }

    // update values
    $('#y1Field').val(newValueY1);
    this.reloadSelection();
  }

  decreaseSelectionSizeFromTop() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) + Math.max(1,(globals.moveSelectionStepSize * globals.imageScaleHeight)));
    let newValueY2 = Math.round(parseInt($('#y2Field').val()));

    if (newValueY2 <= newValueY1) {
      newValueY1 = newValueY2 - 1;
    }
    // update values
    $('#y1Field').val(newValueY1);
    this.reloadSelection();
  }

  increaseSelectionSizeRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleWidth)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension

    if (newValueX2 > Math.round(globals.image.width() * globals.imageScaleWidth)) {
      newValueX2 = Math.ceil(globals.image.width() * globals.imageScaleWidth);
    }
    // update values
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  decreaseSelectionSizeFromRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX1 = Math.round(parseInt($('#x1Field').val()));
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScaleWidth)));

    if (newValueX1 >= newValueX2) {
      newValueX2 = newValueX1 + 1;
    }
    // update values
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  cancelSelection() {
    if (this.selection) {
      this.selection.cancelSelection();
    }
  }

  /**
   * Update the contents of the annotation values
   *
   * @param img
   * @param selection
   */
  updateAnnotationFields(img, selection) {
    let not_in_image_cb = $('#not_in_image');
    if (not_in_image_cb.prop('checked')) {
      $('#not_in_image').prop('checked', false).change();
    }
    // Add missing fields
    let i = 1;
    for (; selection.hasOwnProperty("x" + i); i++) {
      if (!$('#x' + i + 'Field').length) {
        $('#coordinate_table').append(BoundingBoxes.getTag("x" + i)).append(BoundingBoxes.getTag("y" + i));
      }
    }
    // Remove unnecessary fields
    for (; $('#x' + i + 'Field').length; i++) {
      $('#x' + i + 'Box').remove();
      $('#y' + i + 'Box').remove();
    }
    $('#x1Field').val(Math.round(selection.x1 * globals.imageScaleWidth));
    $('#y1Field').val(Math.round(selection.y1 * globals.imageScaleHeight));
    $('#x2Field').val(Math.round(selection.x2 * globals.imageScaleWidth));
    $('#y2Field').val(Math.round(selection.y2 * globals.imageScaleHeight));
  }

  static getTag(field) {
    return '<div id="' + field + 'Box"><div class="col-xs-2" style="max-width: 3em">' +
      '<label for="' + field + 'Field">' + field + '</label>' +
      '</div><div class="col-xs-10">' +
      '<input id="' + field + 'Field" class="Coordinates annotation_value form-control"' +
      'type="text" name="' + field + 'Field" value="0" min="0" disabled>' +
      '</div><div class="col-xs-12"></div></div>';
  }

  reset() {
    this.clear();
  }

  handleMouseDown(event) { }
  handleMouseUp(event) { }
  handleEscape() { this.resetSelection(); }

  handleMouseClick(event) {
    // get current annotation type id
    let annotationType = parseInt($('#annotation_type_id').val());

    // array with all matching annotations
    let matchingAnnotations = [];

    for (let a in globals.currentAnnotations) {
      let annotation = globals.currentAnnotations[a];
      if (annotation.annotation_type.id !== annotationType) {
        continue;
      }
      if (annotation.vector === null)
        continue;

      let left = annotation.vector.x1 / globals.imageScaleWidth;
      let right = annotation.vector.x2 / globals.imageScaleWidth;
      let top = annotation.vector.y1 / globals.imageScaleHeight;
      let bottom = annotation.vector.y2 / globals.imageScaleHeight;

      // check if we clicked inside that annotation
      if (globals.mouseClickX >= left && globals.mouseClickX <= right && globals.mouseClickY >= top && globals.mouseClickY <= bottom) {
        matchingAnnotations.push(annotation);
      }
    }

    // no matches
    if (matchingAnnotations.length === 0) {
      return;
    }

    annotation = matchingAnnotations[0];

    // a single match
    if (matchingAnnotations.length === 1) {
      // get the id of the corresponding edit button
      let edit_button_id = '#annotation_edit_button_' + annotation.id;
      // trigger click event
      $(edit_button_id).click();
    }
    // multiple matches
    else {
      // if we have multiple matching annotations, we have the following descending criteria:
      // 1. prefer annotation lying inside another one completely
      // 2. prefer annotation, which left border is to the left of another ones
      // 3. prefer annotation, which top border is above another ones
      for (let a1 in matchingAnnotations) {
        let annotation1 = matchingAnnotations[a1];

        if (annotation.id === annotation1.id)
          continue;

        if (this.inside(annotation1, annotation)) {
          annotation = annotation1;
          continue;
        }

        if (this.inside(annotation, annotation1)) {
          continue;
        }

        if (this.leftOf(annotation1, annotation)) {
          annotation = annotation1;
          continue;
        }

        if (this.leftOf(annotation, annotation1)) {
          continue;
        }

        if (this.above(annotation1, annotation)) {
          annotation = annotation1;
          continue;
        }

        if (this.above(annotation, annotation1)) {
          continue;
        }
      }
      // get the id of the corresponding edit button
      let edit_button_id = '#annotation_edit_button_' + annotation.id;
      // trigger click event
      $(edit_button_id).click();
    }
  }

  handleMousemove() {}

  // checks if annotation a1 is inside annotation a2
  inside(a1, a2) {
    return a1.vector.x1 >= a2.vector.x1 && a1.vector.y1 >= a2.vector.y1 &&
      a1.vector.x2 <= a2.vector.x2 && a1.vector.y2 <= a2.vector.y2;
  }

  // checks if the left border of annotation a1 is to the left of the left border of annotation a2
  leftOf(a1, a2) {
    return a1.vector.x1 < a2.vector.x1;
  }

  // checks if the top border of annotation a1 is above the top border of annotation a2
  above(a1, a2) {
    return a1.vector.y1 < a2.vector.y1;
  }
}
