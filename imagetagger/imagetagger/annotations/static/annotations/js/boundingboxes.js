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

    if (annotations.length === 0 || !globals.drawAnnotations) {
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
        'top': annotation.vector.y1 / globals.imageScaleHeight,
        'left': annotation.vector.x1 / globals.imageScaleWidth + parseFloat($('img#image').parent().css('padding-left')),
        'width': (annotation.vector.x2 - annotation.vector.x1) / globals.imageScaleWidth,
        'height': (annotation.vector.y2 - annotation.vector.y1) / globals.imageScaleHeight
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
      Math.round($('#x1Field').val() / globals.imageScaleWidth),
      Math.round($('#y1Field').val() / globals.imageScaleHeight),
      Math.round($('#x2Field').val() / globals.imageScaleWidth),
      Math.round($('#y2Field').val() / globals.imageScaleHeight)
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
    $('#not_in_image').prop('checked', false).change();
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
}
