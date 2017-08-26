(function() {
  const API_BASE_URL = '/annotations/api/';
  const STATIC_ROOT = '/static/';
  const FEEDBACK_DISPLAY_TIME = 3000;

  // TODO: Find a solution for url resolvings

  var csrf_token;
  var headers;
  var hideFeedbackTimeout;
  var image;
  var imageId;
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
   * Create an annotation using the form data from the current page.
   *
   * @param event
   */
  function createAnnotation(event) {
    if (event !== undefined) {
      // triggered using an event handler
      event.preventDefault();
    }

    var annotationTypeId = parseInt($('#annotation_type_id').val());
    var vector = null;

    if (!$('#not_in_image').is(':checked')) {
      vector = {
        x1: parseInt($('#x1Field').val()),
        x2: parseInt($('#x2Field').val()),
        y1: parseInt($('#y1Field').val()),
        y2: parseInt($('#y2Field').val())
      }
    }

    if (!validate_vector(vector)) {
      displayFeedback($('#feedback_annotation_invalid'));
      return;
    }

    $('.js_feedback').stop().addClass('hidden');
    $('.annotate_button').prop('disabled', true);
    $.ajax(API_BASE_URL + 'annotation/create/', {
      type: 'POST',
      headers: headers,
      dataType: 'json',
      data: JSON.stringify({
        annotation_type_id: annotationTypeId,
        image_id: imageId,
        vector: vector
      }),
      success: function(data, textStatus, jqXHR) {
        $('.annotate_button').prop('disabled', false);

        if (jqXHR.status === 200) {
          displayFeedback($('#feedback_annotation_exists'));
        } else if (jqXHR.status === 201) {
          displayFeedback($('#feedback_annotation_created'));
          displayExistingAnnotations(data.annotations);
        }

        resetSelection();
      },
      error: function() {
        $('.annotate_button').prop('disabled', false);
        displayFeedback($('#feedback_connection_error'));
      }
    });
  }

  /**
   * Display  existing annotations on current page.
   *
   * @param annotations
   */
  function displayExistingAnnotations(annotations) {
    var annotationsHtml = '';

    // display new annotations
    for (var i = 0; i < annotations.length; i++) {
      var annotation = annotations[i];

      var annotationContent = annotation.content;
      if (annotation.vector !== null) {
        annotationContent = '';
        for (var key in annotation.vector) {
          if (annotationContent !== '') {
            annotationContent += ' &bull; ';
          }
          annotationContent += '<em>' + key + '</em>: ' + annotation.vector[key];
        }
      }

      annotationsHtml += '<div class="annotation">' +
        annotation.annotation_type.name + ':' +
        '<div style="float: right;">' +
        '<a href="/annotations/' + annotation.id + '/verify/">' +
        '<img src="' + STATIC_ROOT + 'symbols/checkmark.png" alt="edit">' +
        '</a> ' +
        '<a href="/annotations/' + annotation.id + '/edit/">' +
        '<img src="' + STATIC_ROOT + 'symbols/pencil.png" alt="edit">' +
        '</a> ' +
        '<a href="/annotations/' + annotation.id + '/delete/">' +
        '<img src="' + STATIC_ROOT + 'symbols/bin.png" alt="delete">' +
        '</a>' +
        '</div>' +
        '<br>' +
        annotationContent +
        '</div>';
    }

    $('#existing_annotations').html(annotationsHtml);
  }

  /**
   * Display a feedback element for a few seconds.
   *
   * @param elem
   */
  function displayFeedback(elem) {
    if (hideFeedbackTimeout !== undefined) {
      clearTimeout(hideFeedbackTimeout);
    }

    elem.removeClass('hidden');

    hideFeedbackTimeout = setTimeout(function() {
      $('.js_feedback').addClass('hidden');
    }, FEEDBACK_DISPLAY_TIME);
  }

  /**
   * Handle toggle of the not in image checkbox.
   *
   * @param event
   */
  function handleNotInImageToggle(event) {
    var coordinate_table = $('#coordinate_table');

    if ($('#not_in_image').is(':checked')) {
      // hide the coordinate selection.
      resetSelection();
      coordinate_table.hide();
    } else {
      coordinate_table.show();
    }
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

    if (selection !== undefined) {
      selection.cancelSelection();
    }
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
    $('#not_in_image').prop('checked', false).change();
  }

  /**
   * Validate a vector.
   *
   * @param vector
   */
  function validate_vector(vector) {
    // TODO: support different vector types

    if (vector === null) {
      // not in image
      return true;
    }

    return vector.x2 - vector.x1 >= 1 && vector.y2 - vector.y1 >= 1
  }

  $(function() {
    image = $('#image');
    mousepos = $('#mousepos');
    mousepos.hide();

    // get current environment
    csrf_token = $('[name="csrfmiddlewaretoken"]').first().val();
    imageId = parseInt($('#image_id').html());
    headers = {
      "Content-Type": 'application/json',
      "X-CSRFTOKEN": csrf_token
    };

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
    $('#not_in_image').on('change', handleNotInImageToggle);
    handleNotInImageToggle();

    $('.js_feedback').click(function() {
      $(this).addClass('hidden');
    });

    // register click events
    $('#reset_button').click(resetSelection);
    $('#save_button').click(createAnnotation);

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
          var notInImage = $('#not_in_image');
          notInImage.prop('checked', !notInImage.is(':checked')).change();
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
