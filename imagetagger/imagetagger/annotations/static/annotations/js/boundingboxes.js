// JS file for bounding box internals

class BoundingBoxes {
  constructor() {
    this.initialized = false;
    this.selection = undefined;
    if (globals.image === '') {
      globals.image = $('#image');
    }
  }
  drawExistingAnnotations(annotations) {
    this.clear();
    calculateImageScale();

    if (annotations.length === 0 || !$('#draw_annotations').prop('checked')) {
      return;
    }

    // clear all boxes
    var boundingBoxes = document.getElementById('boundingBoxes');

    var annotationType = parseInt($('#annotation_type_id').val());

    for (var a in annotations) {

      var annotation = annotations[a];
      if (annotation.annotation_type.id !== annotationType) {
        continue;
      }
      if (annotation.vector === null) {
        continue;
      }

      var boundingBox = document.createElement('div');
      boundingBox.setAttribute('id', 'boundingBox');
      $(boundingBox).css({
        'top': annotation.vector.y1 / globals.imageScale,
        'left': annotation.vector.x1 / globals.imageScale + parseFloat($('img#image').parent().css('padding-left')),
        'width': (annotation.vector.x2 - annotation.vector.x1) / globals.imageScale,
        'height': (annotation.vector.y2 - annotation.vector.y1) / globals.imageScale
      });

      boundingBoxes.appendChild(boundingBox);
    }
  }

  clear() {
    var boundingBoxes = document.getElementById('boundingBoxes');

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
  reloadSelection() {
    this.selection = globals.image.imgAreaSelect({
      instance: true,
      show: true
    });
    this.selection.setSelection(
      Math.round($('#x1Field').val() / globals.imageScale),
      Math.round($('#y1Field').val() / globals.imageScale),
      Math.round($('#x2Field').val() / globals.imageScale),
      Math.round($('#y2Field').val() / globals.imageScale)
    );
    this.selection.update();
  }

  /**
   * Delete current selection.
   */
  resetSelection(abortEdit) {
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
        this.reloadSelection();
      }
    }
    if (reset !== false) {
      globals.restoreSelection = undefined;
    }
  }

  /**
   * Validate a vector.
   *
   * @param vector
   */
  validate_vector(vector) {
    // TODO: support different vector types

    if (vector === null) {
      // not in image
      return true;
    }

    return vector.x2 - vector.x1 >= 1 && vector.y2 - vector.y1 >= 1
  }

  moveSelectionUp() {
    // calculate value +/- stepsize (times stepsize to account for differing image sizes)
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    let newValueY2 = Math.round(parseInt($('#y2Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0) {
      newValueY1 = 0;
      newValueY2 = $('#y2Field').val();
    }
    if (newValueY2 > Math.round(globals.image.height() * globals.imageScale)) {
      newValueY2 = Math.ceil(globals.image.height() * globals.imageScale);
      newValueY1 = $('#y1Field').val();
    }
    // update values
    $('#y1Field').val(newValueY1);
    $('#y2Field').val(newValueY2);
    this.reloadSelection();
  }

  moveSelectionDown() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    let newValueY2 = Math.round(parseInt($('#y2Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0) {
      newValueY1 = 0;
      newValueY2 = $('#y2Field').val();
    }
    if (newValueY2 > Math.round(globals.image.height() * globals.imageScale)) {
      newValueY2 = Math.ceil(globals.image.height() * globals.imageScale);
      newValueY1 = $('#y1Field').val();
    }
    // update values
    $('#y1Field').val(newValueY1);
    $('#y2Field').val(newValueY2);
    this.reloadSelection();
  }

  moveSelectionRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX1 = Math.round(parseInt($('#x1Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0) {
      newValueX1 = 0;
      newValueX2 = $('#x2Field').val();
    }
    if (newValueX2 > Math.round(globals.image.width() * globals.imageScale)) {
      newValueX2 = Math.ceil(globals.image.width() * globals.imageScale);
      newValueX1 = $('#x1Field').val();
    }
    // update values
    $('#x1Field').val(newValueX1);
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  moveSelectionLeft() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX1 = Math.round(parseInt($('#x1Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0) {
      newValueX1 = 0;
      newValueX2 = $('#x2Field').val();
    }
    if (newValueX2 > Math.round(globals.image.width() * globals.imageScale)) {
      newValueX2 = Math.ceil(globals.image.width() * globals.imageScale);
      newValueX1 = $('#x1Field').val();
    }
    // update values
    $('#x1Field').val(newValueX1);
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  increaseSelectionSizeUp() {
    // calculate value +/- stepsize (times stepsize to account for differing image sizes)
    let newValueY1 = Math.round(parseInt($('#y1Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0) {
      newValueY1 = 0;
    }

    // update values
    $('#y1Field').val(newValueY1);
    this.reloadSelection();
  }

  decreaseSelectionSizeDown() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueY1 = Math.round(parseInt($('#y1Field').val()));
    let newValueY2 = Math.round(parseInt($('#y2Field').val()) - Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY2 < 0) {
      newValueY2 = 1;
    }
    if (newValueY2 <= newValueY1) {
      newValueY2 = newValueY1 + Math.round(Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    }
    // update values
    $('#y2Field').val(newValueY2);
    this.reloadSelection();
  }

  increaseSelectionSizeRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX2 = Math.round(parseInt($('#x2Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension

    if (newValueX2 > Math.round(globals.image.width() * globals.imageScale)) {
      newValueX2 = Math.ceil(globals.image.width() * globals.imageScale);
    }
    // update values
    $('#x2Field').val(newValueX2);
    this.reloadSelection();
  }

  decreaseSelectionSizeLeft() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    let newValueX1 = Math.round(parseInt($('#x1Field').val()) + Math.max(1, (globals.moveSelectionStepSize * globals.imageScale)));
    let newValueX2 = Math.round(parseInt($('#x2Field').val()));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0) {
      newValueX1 = 0;
    }
    if (newValueX1 >= newValueX2) {
      newValueX1 = newValueX2 - 1;
    }
    // update values
    $('#x1Field').val(newValueX1);
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
    $('#x1Field').val(Math.round(selection.x1 * globals.imageScale));
    $('#y1Field').val(Math.round(selection.y1 * globals.imageScale));
    $('#x2Field').val(Math.round(selection.x2 * globals.imageScale));
    $('#y2Field').val(Math.round(selection.y2 * globals.imageScale));
    $('#not_in_image').prop('checked', false).change();
  }
  reset() {
    this.clear();
  }
}
