(function() {
  var image;
  var imageScale = 0;
  var initialized = false;
  var mousepos;
  var selection;

  /**
   * Calculate the correct imageScale value.
   */
  function calculateImageScale() {
    imageScale = image.get(0).naturalWidth / image.width();
  }

  /**
   * Handle a selection using the mouse.
   *
   * @param event
   */
  function handleSelection(event) {
    calculateImageScale();
    var cH = $('#crosshair-h'), cV = $('#crosshair-v');
    var position = image.offset();
    if (event.pageX > position.left &&
          event.pageX < position.left + image.width() &&
          event.pageY > position.top &&
          event.pageY < position.top + image.height()) {
      cH.show();
      cV.show();
      mousepos.show();

      cH.css('top', event.pageY + 1);
      cV.css('left', event.pageX + 1);
      cV.css('height', image.height() - 1);
      cV.css('margin-top', position.top);
      cH.css('width', image.width() - 1);
      cH.css('margin-left', position.left);

      mousepos.css({
        top: (event.pageY) + 'px',
        left: (event.pageX)  + 'px'
      }, 800);
      mousepos.text(
        '(' + Math.round((event.pageX - position.left) * imageScale) + ', ' +
        Math.round((event.pageY - position.top) * imageScale) + ')');
      event.stopPropagation();
    }
    else{
      cH.hide();
      cV.hide();
      mousepos.hide();
    }
  }

  /**
   * Handle a resize event of the window.
   *
   * @param event
   */
  function handleResize() {
    selection.cancelSelection();
    calculateImageScale();
  }

  /**
   * Initialize the selection.
   */
  function initSelection() {
    initialized = true;

    selection = image.imgAreaSelect({
      instance: true,
      show: true,
      minHeight: 2,
      minWidth: 2,
      onSelectChange: updateAnnotationFields
    });
    selection.cancelSelection();
  }

  /**
   * Reload the selection.
   */
  function reloadSelection() {
    selection = image.imgAreaSelect({
      instance: true,
      show: true
    });
    selection.setSelection(
      Math.round($('#x1Field').val() / imageScale),
      Math.round($('#y1Field').val() / imageScale),
      Math.round($('#x2Field').val() / imageScale),
      Math.round($('#y2Field').val() / imageScale)
    );
    selection.update();
  }

  /**
   * Delete current selection.
   */
  function resetSelection() {
    $('.annotation_value').val(0);

    selection.cancelSelection();
  }

  /**
   * Update the contents of the annotation values
   *
   * @param img
   * @param selection
   */
  function updateAnnotationFields(img, selection) {
    $('#x1Field').val(Math.ceil(selection.x1 * imageScale));
    $('#y1Field').val(Math.ceil(selection.y1 * imageScale));
    $('#x2Field').val(Math.floor(selection.x2 * imageScale));
    $('#y2Field').val(Math.floor(selection.y2 * imageScale));
  }

  $(function() {
    image = $('#image');
    mousepos = $('#mousepos');
    mousepos.hide();

    // W3C standards do not define the load event on images, we therefore need to use
    // it from window (this should wait for all external sources including images)
    $(window).on('load', initSelection);

    setTimeout(function() {
      // Fallback if window load initialization did not succeed
      if (!initialized) {
        console.log('fallback solution for selection initialization used!');
        initSelection();
        // TODO: Get rid of this
        // This is used to load an existing annotation in the edit view
        if (typeof loadannotation === "function") {
          loadannotation();
          reloadSelection();
        }
      }
    }, 1000);

    $('.annotation_value').on('input', function() {
      reloadSelection();
    });

    $('#reset_button').click(resetSelection);

    $(document).on('mousemove touchmove', handleSelection);
    $(window).on('resize', handleResize);


    // TODO: this should be done only for the annotate view
    $(document).keyup(function(event) {
      switch (event.keyCode){
        case 70: //f
          $('#next_button').click();
          break;
        case 68: //d
          $('#skip_button').click();
          break;
        case 83: //s
          $('#back_button').click();
          break;
        case 65: //a
          $('#last_button').click();
          break;
        case 71: //g
          var nii = $('#not_in_image');
          if(nii.prop('checked')) {
            nii.prop('checked', false)
          }
          else {
            nii.prop('checked', true)
          }
          break;
        case 82: //r
          $('#reset_button').click();
          break;
        case 86: //'v'
          $('#annotation_form').submit();
          break;
      }
    });

    // TODO: Get rid of this
    // This is used to load an existing annotation in the edit view
    if (typeof loadannotation === "function") {
      loadannotation();
      reloadSelection();
    }

    // TODO: Get rid of this
    if (typeof init_navigationbuttons === "function") {
      init_navigationbuttons();
      reloadSelection();
    }
  });
})();
