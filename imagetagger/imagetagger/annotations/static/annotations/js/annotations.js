globals = {
  image: {},
  imageScaleWidth: 1,
  imageScaleHeight: 1,
  restoreSelection: undefined,
  restoreSelectionVectorType: 1,
  restoreSelectionNodeCount: 0,
  moveSelectionStepSize: 2,
  drawAnnotations: true,
  mouseUpX: undefined,
  mouseUpY: undefined,
  mouseClickX: undefined,
  mouseClickY: undefined,
  mouseDownX: undefined,
  mouseDownY: undefined,
  currentAnnotationsOfSelectedType: undefined,
  stdColor: '#CC4444',
  mutColor: '#CC0000'
};

/**
 * Calculate the correct imageScale value.
 */
function calculateImageScale() {
  globals.imageScaleWidth = globals.image.get(0).naturalWidth / globals.image.width();
  globals.imageScaleHeight = globals.image.get(0).naturalHeight / globals.image.height();
}

(function() {
  const API_ANNOTATIONS_BASE_URL = '/annotations/api/';
  const API_IMAGES_BASE_URL = '/images/api/';
  const FEEDBACK_DISPLAY_TIME = 3000;
  const ANNOTATE_URL = '/annotations/%s/';
  const IMAGE_SET_URL = '/images/imageset/%s/';
  const DELETE_IMAGE_URL = '/images/image/delete/%s/';
  const PRELOAD_BACKWARD = 2;
  const PRELOAD_FORWARD = 5;
  const STATIC_ROOT = '/static/';

  let gCsrfToken;
  let gHeaders;
  let gHideFeedbackTimeout;
  let gImageCache = {};
  let gImageId;
  let gImageSetId;
  let gImageList;
  let gMousepos;
  let gAnnotationType = -1;
  let gCurrentAnnotations = [];
  let gHighlightedAnnotation;
  let gShiftDown;
  let tool;
  let gEditAnnotationId;  // id of the currently edited annotation, or undefined

  function shorten(string, length) {
    let threshold = length || 30;
    if (string.length < threshold) {
      return string;
    } else {
      return string.substr(0, threshold / 2 - 1) + '...' + string.substr(-threshold / 2 + 2, threshold / 2 - 2);
    }
  }

  function setTool() {
    let selected_annotation = $('#annotation_type_id').children(':selected').data();
    let vector_type = selected_annotation.vectorType;
    let node_count = selected_annotation.nodeCount;
    let annotationTypeId = parseInt($('#annotation_type_id').children(':selected').val());
    if (tool && tool.annotationTypeId === annotationTypeId) {
      // Tool does not have to change
      return;
    }
    if (tool) {
      tool.resetSelection();
      tool.cancelSelection();
      tool.initSelection();
      tool.reset();
      delete tool;
    }
    $('#feedback_multiline_information').addClass('hidden');
    switch (vector_type) {
      case 1: // Bounding Box
        // Remove unnecessary number fields
        for (let i = 3; $('#x' + i + 'Field').length; i++) {
          $('#x' + i + 'Box').remove();
          $('#y' + i + 'Box').remove();
        }
        tool = new BoundingBoxes(annotationTypeId);
        $('#image_canvas').addClass('hidden');
        $('.hair').removeClass('hidden');
        $('#image').css('cursor', 'none');
        $('.imgareaselect-outer').css('cursor', 'none');
        break;
      case 4: // Multiline, fallthrough
        $('#feedback_multiline_information').removeClass('hidden');
      case 2: // Point, fallthrough
      case 3: // Line, fallthrough
      case 5: // Polygon
        $('#image_canvas').removeClass('hidden').attr('width', Math.ceil($('#image').width())).attr('height', Math.ceil($('#image').height()));
        tool = new Canvas($('#image_canvas'), vector_type, node_count, annotationTypeId);
        $('.hair').addClass('hidden');
        $('#image_canvas').css('cursor', 'crosshair');
        break;
      default:
        // Dummytool
        tool = {
          initSelection: function() {},
          resetSelection: function() {},
          restoreSelection: function() {},
          cancelSelection: function() {},
          reset: function() {},
          drawExistingAnnotations: function() {},
          closeDrawing: function() {},
          handleMousemove: function() {},
          handleMouseDown: function() {},
          handleMouseUp: function() {},
          handleMouseClick: function() {},
          moveSelectionLeft: function() {},
          moveSelectionRight: function() {},
          moveSelectionUp: function() {},
          moveSelectionDown: function() {},
          decreaseSelectionSizeFromRight: function() {},
          decreaseSelectionSizeFromTop: function() {},
          increaseSelectionSizeRight: function() {},
          increaseSelectionSizeUp: function() {},
          setHighlightColor: function() {},
          unsetHighlightColor: function() {}
        };
    }
    if (globals.currentAnnotationsOfSelectedType) {
      tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);
    }
    console.log("Using tool " + tool.constructor.name);
  }

  /**
   * Check whether the current state allows to create an annotation (i.e. a valid selection was made)
   * @param markForRestore if the annotation should be saved to be reused for the next image
   * @return the valid vector or null
   */
  function getValidAnnotation(markForRestore) {
    let annotationTypeId = parseInt($('#annotation_type_id').val());
    let vector = null;

    if (annotationTypeId === -1) {
      displayFeedback($('#feedback_annotation_type_missing'));
      throw new Error('annotation type missing');
    }
    let blurred = $('#blurred').is(':checked');
    let concealed = $('#concealed').is(':checked');
    if (!$('#not_in_image').is(':checked')) {
      vector = {};
      for (let i = 1; $('#x' + i + 'Field').length; i++) {
        vector["x" + i] = parseInt($('#x' + i + 'Field').val());
        vector["y" + i] = parseInt($('#y' + i + 'Field').val());
      }
      // Swap points if the second one is left of the first one
      if (Object.keys(vector).length === 4) {
        if (vector.x1 > vector.x2 || vector.x1 === vector.x2 && vector.y1 > vector.y2) {
          let tmp_x1 = vector.x2;
          let tmp_y1 = vector.y2;
          vector.x2 = vector.x1;
          vector.y2 = vector.y1;
          vector.x1 = tmp_x1;
          vector.y1 = tmp_y1;
        }
      }
    }

    let selected_annotation = $('#annotation_type_id').children(':selected').data();
    let vector_type = selected_annotation.vectorType;
    let node_count = selected_annotation.nodeCount;
    if (!validate_vector(vector, vector_type, node_count)) {
      displayFeedback($('#feedback_annotation_invalid'));
      throw new Error('annotation is invalid');
    }

    if (markForRestore === true) {
      globals.restoreSelection = vector;
      globals.restoreSelectionVectorType = vector_type;
      globals.restoreSelectionNodeCount = node_count;
    }

    let annotation = {
      annotation_type_id: annotationTypeId,
      image_id: gImageId,
      vector: vector,
      concealed: concealed,
      blurred: blurred
    };
    if (gEditAnnotationId !== undefined) {
      annotation.annotation_id = gEditAnnotationId;
    }
    return annotation;
  }

  /**
   * Create an annotation using the form data from the current page.
   * If an annotation is currently edited, an update is triggered instead.
   *
   * @param annotation the annotation to be created, as returned by getValidAnnotation
   */
  async function createAnnotation(annotation) {

    let action = 'create';
    let body = annotation;
    let editing = false;
    if (body.annotation_id !== undefined) {
      // edit instead of create
      action = 'update';
      editing = true;
    }

    $('.js_feedback').stop().addClass('hidden');
    $('.annotate_button').prop('disabled', true);
    try {
      let response = await fetch(API_ANNOTATIONS_BASE_URL + 'annotation/' + action + '/', {
        method: 'POST',
        headers: gHeaders,
        body: JSON.stringify(body),
      });

      let data = await response.json();
      if (response.status === 200) {
        if (editing) {
          if (data.detail === 'similar annotation exists.') {
            displayFeedback($('#feedback_annotation_exists_deleted'));
            $('#annotation_edit_button_' + gEditAnnotationId).parent().parent().fadeOut().remove();
          } else {
            displayFeedback($('#feedback_annotation_updated'));
            displayExistingAnnotations(data.annotations);
            tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);
          }
        } else {
          displayFeedback($('#feedback_annotation_exists'));
        }
      } else if (response.status === 201) {
        displayFeedback($('#feedback_annotation_created'));
        displayExistingAnnotations(data.annotations);
      }
      // update current annotations
      gCurrentAnnotations = data.annotations;
      globals.currentAnnotationsOfSelectedType = gCurrentAnnotations.filter(function (e) {
        return e.annotation_type.id === gAnnotationType;
      });

      tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);

      resetSelection();
    } catch (e) {
      console.log(e);
      displayFeedback($('#feedback_connection_error'));
    } finally {
      $('.annotate_button').prop('disabled', false);
    }
  }

  async function loadAnnotationTypeList() {
    try {
      let response = await fetch(API_ANNOTATIONS_BASE_URL + 'annotation/loadannotationtypes/', {
        method: 'GET',
        headers: gHeaders,
      });
      let data = await response.json();
      displayAnnotationTypeOptions(data.annotation_types);
    } catch {
      displayFeedback($('#feedback_connection_error'))
    }
  }

  function displayAnnotationTypeOptions(annotationTypeList) {
    // TODO: empty the options?
    let annotationTypeFilterSelect = $('#filter_annotation_type');
    let annotationTypeToolSelect = $('#annotation_type_id');
    $.each(annotationTypeList, function (key, annotationType) {
      annotationTypeToolSelect.append($('<option/>', {
        name: annotationType.name,
        value: annotationType.id,
        html: annotationType.name + ' (' + (key + 1) + ')',
        id: 'annotation_type_' + (key + 1),
        'data-vector-type': annotationType.vector_type,
        'data-node-count': annotationType.node_count,
        'data-blurred': annotationType.enable_blurred,
        'data-concealed': annotationType.enable_concealed,
      }));
      annotationTypeFilterSelect.append($('<option/>', {
        name: annotationType.name,
        value: annotationType.id,
        html: annotationType.name
      }));
    });
  }

  /**
   * Delete an annotation.
   *
   * @param annotationId
   */
  async function deleteAnnotation(annotationId) {
    // TODO: Do not use a primitive js confirm
    if (!confirm('Do you really want to delete the annotation?')) {
      return;
    }

    if (gEditAnnotationId === annotationId) {
      // stop editing
      resetSelection();
      $('#not_in_image').prop('checked', false).change();
    }

    $('.js_feedback').stop().addClass('hidden');
    let params = {
      annotation_id: annotationId
    };

    $('.annotate_button').prop('disabled', true);
    try {
      let response = await fetch(API_ANNOTATIONS_BASE_URL + 'annotation/delete/?' + $.param(params), {
        method: 'DELETE',
        headers: gHeaders,
      });
      let data = await response.json();
      gCurrentAnnotations = data.annotations;
      globals.currentAnnotationsOfSelectedType = gCurrentAnnotations.filter(function (e) {
        return e.annotation_type.id === gAnnotationType;
      });
      // redraw the annotations
      tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);
      displayExistingAnnotations(gCurrentAnnotations);
      displayFeedback($('#feedback_annotation_deleted'));
      gEditAnnotationId = undefined;
    } catch {
      displayFeedback($('#feedback_connection_error'));
    } finally {
      $('.annotate_button').prop('disabled', false);
    }
  }

  /**
   * Display  existing annotations on current page.
   *
   * @param annotations
   */
  function displayExistingAnnotations(annotations) {
    let existingAnnotations = $('#existing_annotations');
    let noAnnotations = $('#no_annotations');

    existingAnnotations.addClass('hidden');

    if (annotations.length === 0) {
      noAnnotations.removeClass('hidden');
      return;
    }

    noAnnotations.addClass('hidden');
    existingAnnotations.html('');

    // display new annotations
    for (let i = 0; i < annotations.length; i++) {
      let annotation = annotations[i];

      let alertClass = '';
      if (gEditAnnotationId === annotation.id) {
        alertClass = ' alert-info';
      }
      let newAnnotation = $(
        '<div id="annotation_' + annotation.id +
        '" class="annotation' + alertClass + '">');

      if (annotation.vector !== null) {
        annotation.content = '';
        for (let i = 1; annotation.vector.hasOwnProperty("x" + i); i++) {
          if (annotation.content !== '') {
            annotation.content += ' &bull; ';
          }
          if (i === 4) {
            // Show no more than three points
            annotation.content += '...';
            break;
          }
          annotation.content += 'x' + i + ': ' + annotation.vector["x" + i];
          annotation.content += ' &bull; ';
          annotation.content += 'y' + i + ': ' + annotation.vector["y" + i];
        }
      } else {
        annotation.content = 'not in image';
      }
      if (annotation.blurred) {
        annotation.content += ' <span id="blurred_label" class="label label-info">Blurred</span>';
      }

      if (annotation.concealed) {
        annotation.content += ' <span id="concealed_label" class="label label-warning">Concealed</span>';
      }

      newAnnotation.append(annotation.annotation_type.name + ':');

      let annotationLinks = $('<div style="float: right;">');
      let verifyButton = $('<a href="/annotations/' + annotation.id + '/verify/">' +
      '<img src="' + STATIC_ROOT + 'symbols/checkmark.png" alt="verify" class="annotation_verify_button">' +
      '</a>');
      let editButton = $('<a href="#">' +
      '<img src="' + STATIC_ROOT + 'symbols/pencil.png" alt="edit" class="annotation_edit_button">' +
      '</a>');
      let deleteButton = $('<a href="/annotations/' + annotation.id + '/delete/">' +
      '<img src="' + STATIC_ROOT + 'symbols/bin.png" alt="delete" class="annotation_delete_button">' +
      '</a>');
      const annotationId = annotation.id;
      editButton.attr('id', 'annotation_edit_button_' + annotationId);
      editButton.click(function(event) {
        editAnnotation(this, annotationId);
      });
      editButton.data('annotationtypeid', annotation.annotation_type.id);
      editButton.data('annotationid', annotation.id);
      editButton.data('vector', annotation.vector);
      editButton.data('blurred', annotation.blurred);
      editButton.data('concealed', annotation.concealed);
      deleteButton.click(async function(event) {
        event.preventDefault(); // the button is a link, don't follow it
        await deleteAnnotation(annotationId);
      });
      annotationLinks.append(verifyButton);
      annotationLinks.append(' ');
      annotationLinks.append(editButton);
      annotationLinks.append(' ');
      annotationLinks.append(deleteButton);

      newAnnotation.append(annotationLinks);
      newAnnotation.append('<br>');
      newAnnotation.append(annotation.content);

      existingAnnotations.append(newAnnotation);
    }

    existingAnnotations.removeClass('hidden');
  }

  /**
   * Highlight one annotation in a different color
   * @param annotationTypeId
   * @param annotationId
   */

  function handleMouseClick(e) {
    if (e && (e.target.id === 'image' || e.target.id === 'image_canvas')) {
      let position = globals.image.offset();
      globals.mouseClickX = Math.round((e.pageX - position.left));
      globals.mouseClickY = Math.round((e.pageY - position.top));
      tool.handleMouseClick(e);
    }

    // remove any existing highlight
    if (e.target.className !== 'annotation_edit_button') {
      $('.annotation').removeClass('alert-info');
      if (gHighlightedAnnotation) {
        tool.unsetHighlightColor(gHighlightedAnnotation, globals.currentAnnotationsOfSelectedType.filter(function(element) {
          return element.id === gHighlightedAnnotation;
        }));
        gHighlightedAnnotation = undefined;
      }
    } else {
      // when the click was on the annotation edit button corresponding to the
      // currently highlighted annotation, do not remove the blue highlight
      if (gHighlightedAnnotation && gHighlightedAnnotation !== $(e.target).parent().data('annotationid')) {
        tool.unsetHighlightColor(gHighlightedAnnotation, globals.currentAnnotationsOfSelectedType.filter(function(element) {
          return element.id === gHighlightedAnnotation;
        }));
        gHighlightedAnnotation = undefined;
      }
    }

    // create a new highlight if the click was on an annotation
    if (e.target.className === 'annotation') {
      let editButton = $(e.target).find('.annotation_edit_button').parent();
      $('#annotation_type_id').val(editButton.data('annotationtypeid'));
      handleAnnotationTypeChange();
      tool.setHighlightColor(editButton.data('annotationid'));
      gHighlightedAnnotation = editButton.data('annotationid');
      $(e.target).addClass('alert-info');
    }
  }

  /**
   * Display an image from the image cache or the server.
   *
   * @param imageId
   */
  async function displayImage(imageId) {
    imageId = parseInt(imageId);

    if (gImageList.indexOf(imageId) === -1) {
      console.log(
        'skiping request to load image ' + imageId +
        ' as it is not in current image list.');
      return;
    }

    if (gImageCache[imageId] === undefined) {
      // image is not available in cache. Load it.
      await loadImageToCache(imageId);
    }

    // image is in cache.
    let currentImage = globals.image;
    let newImage = gImageCache[imageId];

    currentImage.attr('id', '');
    newImage.attr('id', 'image');
    gImageId = imageId;
    let loadImages = preloadImages();

    currentImage.replaceWith(newImage);
    globals.image = newImage;
    calculateImageScale();
    tool.initSelection();
    resetSelection();

    if (currentImage.data('imageid') !== undefined) {
      // add previous image to cache
      gImageCache[currentImage.data('imageid')] = currentImage;
    }
    await loadImages;
  }

  /**
   * Delete the current selection
   */
  function resetSelection() {
    tool.resetSelection();
    gEditAnnotationId = undefined;
    $('.annotation').removeClass('alert-info');
    $('#edit_active').addClass('hidden');
  }

  /**
   * Display the images of an image list.
   *
   * @param imageList
   */
  async function displayImageList(imageList) {
    let oldImageList = $('#image_list');
    let result = $('<div>');
    let imageContained = false;

    oldImageList.html('');

    for (let i = 0; i < imageList.length; i++) {
      let image = imageList[i];

      let link = $('<a>');
      link.attr('id', 'annotate_image_link_' + image.id);
      link.attr('href', ANNOTATE_URL.replace('%s', image.id));
      link.addClass('annotate_image_link');
      if (image.id === gImageId) {
        link.addClass('active');
        imageContained = true;
      }
      link.text(image.name);
      link.data('imageid', image.id);
      link.click(async function(event) {
        event.preventDefault(); // do not let the browser follow the link
        await loadAnnotateView($(this).data('imageid'));
      });

      result.append(link);
    }

    oldImageList.attr('id', '');
    result.attr('id', 'image_list');
    oldImageList.replaceWith(result);

    gImageList = getImageList();

    // load first image if current image is not within image set
    if (!imageContained) {
      await loadAnnotateView(imageList[0].id);
    }

    scrollImageList();
  }

  /**
   * Display a feedback element for a few seconds.
   *
   * @param elem
   */
  function displayFeedback(elem) {
    if (gHideFeedbackTimeout !== undefined) {
      clearTimeout(gHideFeedbackTimeout);
    }

    elem.removeClass('hidden');

    gHideFeedbackTimeout = setTimeout(function() {
      $('.js_feedback').addClass('hidden');
    }, FEEDBACK_DISPLAY_TIME);
  }

  /**
   * Edit an annotation.
   *
   * @param annotationElem the element which stores the edit button of the annotation
   * @param annotationId
   */
  function editAnnotation(annotationElem, annotationId) {
    annotationElem = $(annotationElem);
    let annotationTypeId = annotationElem.data('annotationtypeid');
    $('#annotation_type_id').val(annotationTypeId);
    handleAnnotationTypeChange();
    gEditAnnotationId = annotationId;
    $('#edit_active').removeClass('hidden');

    $('.js_feedback').stop().addClass('hidden');
    let params = {
      annotation_id: annotationId
    };

    let annotationData = annotationElem.data('vector');
    if (annotationData === undefined) {
      annotationData = annotationElem.data('escapedvector');
    }

    // highlight currently edited annotation
    $('.annotation').removeClass('alert-info');
    annotationElem.parent().parent().addClass('alert-info');

    let notInImage = $('#not_in_image');
    if (annotationData === null) {
      // not in image
      notInImage.prop('checked', true).change();
      return;
    }

    $('#annotation_type_id').val(annotationTypeId);

    notInImage.prop('checked', false).change();


    tool.reloadSelection(annotationId, annotationData);
    $('#concealed').prop('checked', annotationElem.data('concealed')).change();
    $('#blurred').prop('checked', annotationElem.data('blurred')).change();
  }

  /**
   * Get the image list from all .annotate_image_link within #image_list.
   */
  function getImageList() {
    let imageList = [];
    $('#image_list').find('.annotate_image_link').each(function(key, elem) {
      let imageId = parseInt($(elem).data('imageid'));
      if (imageList.indexOf(imageId) === -1) {
        imageList.push(imageId);
      }
    });

    return imageList;
  }

  /**
   * Validate a vector.
   *
   * @param vector
   * @param vector_type
   * @param node_count
   */
  function validate_vector(vector, vector_type, node_count) {
    if (vector === null) {
      // not in image
      return true;
    }
    let len = Object.keys(vector).length;
    switch (vector_type) {
      case 1: // Ball (Boundingbox)
        return vector.x2 - vector.x1 >= 1 && vector.y2 - vector.y1 >= 1 && len === 4;
      case 2: // Point
        return vector.hasOwnProperty('x1') && vector.hasOwnProperty('y1') && len === 2 && !(vector.x1 === 0 && vector.y1 === 0);
      case 3: // Line
        return vector.x1 !== vector.x2 || vector.y1 !== vector.y2 && len === 4;
      case 4: // Multiline
        // a multiline should have at least two points
        if (len < 4) {
          return false;
        }
        for (let i = 1; i < len / 2 + 1; i++) {
          for (let j = 1; j < len / 2 + 1; j++) {
            if (i !== j && vector['x' + i] === vector['x' + j] && vector['y' + i] === vector['y' + j]) {
              return false;
            }
          }
        }
        return true;
      case 5: // Polygon
        if (len < 6) {
          // A polygon should have at least three points
          return false;
        }
        if (node_count !== 0 && node_count !== (len / 2)) {
          return false;
        }
        for (let i = 1; i <= len / 2; i++) {
          for (let j = 1; j <= len / 2; j++) {
            if (i !== j && vector["x" + i] === vector["x" + j] && vector["y" + i] === vector["y" + j]) {
              return false;
            }
          }
        }
        return true;
    }
    return false;
  }

  function setupCBCheckboxes() {
    let concealed = $('#concealed');
    let concealedP = $('#concealed_p');
    let blurred = $('#blurred');
    let blurredP = $('#blurred_p');
    if ($('#not_in_image').is(':checked')) {
      concealedP.hide();
      concealed.prop('checked', false);
      concealed.prop('disabled', true);
      blurredP.hide();
      blurred.prop('checked', false);
      blurred.prop('disabled', true);
    } else {
      let selectedAnnotation = $('#annotation_type_id').find(':selected');
      if (selectedAnnotation.data('concealed')) {
        concealedP.show();
        concealed.prop('disabled', false);
      } else {
        concealedP.hide();
        concealed.prop('disabled', true);
      }
      if (selectedAnnotation.data('blurred')) {
        blurredP.show();
        blurred.prop('disabled', false);
      } else {
        blurredP.hide();
        blurred.prop('disabled', true);
      }
    }
  }

  /**
   * Handle toggle of the not in image checkbox.
   *
   * @param event
   */
  function handleNotInImageToggle(event) {
    let coordinate_table = $('#coordinate_table');

    if ($('#not_in_image').is(':checked')) {
      // hide the coordinate selection.
      resetSelection();
      coordinate_table.hide();
    } else {
      coordinate_table.show();
    }
    setupCBCheckboxes();
  }

  /**
   * Handle toggle of the draw annotations checkbox.
   *
   * @param event
   */
  function handleShowAnnotationsToggle(event) {
    globals.drawAnnotations = $('#draw_annotations').is(':checked');
    if (globals.drawAnnotations) {
      tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);
    } else {
      tool.clear();
    }
  }

  /**
   * Handle a selection using the mouse.
   *
   * @param event
   */
  function handleSelection(event) {
    calculateImageScale();
    let cH = $('#crosshair-h'), cV = $('#crosshair-v');
    let position = globals.image.offset();
    if (event.pageX > position.left &&
          event.pageX < position.left + globals.image.width() &&
          event.pageY > position.top &&
          event.pageY < position.top + globals.image.height()) {
      cH.show();
      cV.show();
      gMousepos.show();

      cH.css('top', event.pageY + 1);
      cV.css('left', event.pageX + 1);
      cV.css('height', globals.image.height() - 1);
      cV.css('margin-top', position.top);
      cH.css('width', globals.image.width() - 1);
      cH.css('margin-left', position.left);

      gMousepos.css({
        top: (event.pageY) + 'px',
        left: (event.pageX)  + 'px'
      }, 800);
      gMousepos.text(
        '(' + Math.round((event.pageX - position.left) * globals.imageScaleWidth) + ', ' +
        Math.round((event.pageY - position.top) * globals.imageScaleHeight) + ')');
      event.stopPropagation();
    }
    else{
      cH.hide();
      cV.hide();
      gMousepos.hide();
    }
    tool.handleMousemove(event);
  }

  /**
   * Handle a resize event of the window.
   */
  function handleResize() {
    tool.cancelSelection();
    calculateImageScale();
    tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);
  }

  /**
   * Load the annotation view for another image.
   *
   * @param imageId
   * @param fromHistory
   */
  async function loadAnnotateView(imageId, fromHistory) {
    gEditAnnotationId = undefined;

    imageId = parseInt(imageId);

    if (gImageList.indexOf(imageId) === -1) {
      console.log(
        'skiping request to load image ' + imageId +
        ' as it is not in current image list.');
      return;
    }

    let noAnnotations = $('#no_annotations');
    let existingAnnotations = $('#existing_annotations');
    let loading = $('#annotations_loading');
    existingAnnotations.addClass('hidden');
    noAnnotations.addClass('hidden');
    loading.removeClass('hidden');
    $('#annotation_type_id').val(gAnnotationType);

    if (tool instanceof BoundingBoxes) {
      tool.cancelSelection();
    }
    let loadImage = displayImage(imageId).then(scrollImageList);

    if (!$('#keep_selection').prop('checked')) {
      $('#concealed').prop('checked', false);
      $('#blurred').prop('checked', false);
    }

    $('.annotate_image_link').removeClass('active');
    let link = $('#annotate_image_link_' + imageId);
    link.addClass('active');
    $('#active_image_name').text(link.text().trim());
    let next_image_id = gImageList[gImageList.indexOf(imageId) + 1];
    if (gImageList.length !== 1 && next_image_id === undefined) {
      next_image_id = gImageList[0];
    }
    $('#next-image-id').attr('value', next_image_id || '');
    $('#delete-image-form').attr('action', DELETE_IMAGE_URL.replace('%s', imageId));
    tool.restoreSelection(false);

    if (fromHistory !== true) {
      history.pushState({
        imageId: imageId
      }, document.title, '/annotations/' + imageId + '/');
    }

    try {
      // load existing annotations for this image
      await loadAnnotations(imageId);

      loading.addClass('hidden');
      displayExistingAnnotations(gCurrentAnnotations);
      tool.drawExistingAnnotations(globals.currentAnnotationsOfSelectedType);

      if (globals.restoreSelection !== undefined) {
        tool.restoreSelection();
      } else {
        resetSelection();
      }
    } catch {
      console.log("Unable to load annotations for image" + imageId);
    }
    await loadImage;
  }

  /**
   * Load the image list from tye server applying a new filter.
   */
  async function loadImageList() {
    let filterElem = $('#filter_annotation_type');
    let filter = filterElem.val();
    let params = {
      image_set_id: gImageSetId
    };

    // select the corresponding annotation type for the label tool
    if (filter !== '' && !isNaN(filter)) {
      params.filter_annotation_type_id = filter;
      $('#annotation_type_id').val(filter);
      handleAnnotationTypeChange();
    }

    $('.annotate_button').prop('disabled', true);
    try {
      let response = await fetch(API_IMAGES_BASE_URL + 'imageset/load/?' + $.param(params), {
        method: 'GET',
        headers: gHeaders,
      });
      let data = await response.json();
      if (data.image_set.images.length === 0) {
        // set is empty, reset filter
        displayFeedback($('#feedback_image_set_empty'));
        filterElem.val('').change();
      } else {
        await displayImageList(data.image_set.images);
      }
    } catch {
      displayFeedback($('#feedback_connection_error'));
    } finally {
      $('.annotate_button').prop('disabled', false);
    }
  }

  /**
   * Load an image to the cache if it is not in it already.
   *
   * @param imageId
   */
  async function loadImageToCache(imageId) {
    imageId = parseInt(imageId);

    if (gImageList.indexOf(imageId) === -1) {
      console.log(
        'skiping request to load image ' + imageId +
        ' as it is not in current image list.');
      return;
    }

    if (gImageCache[imageId] !== undefined) {
      // already cached
      return;
    }

    gImageCache[imageId] = $('<img>');
    gImageCache[imageId].data('imageid', imageId).attr(
      'src', '/images/image/' + imageId + '/');
  }

  /**
   * Load the annotations of an image to the cache if they are not in it already.
   *
   * @param imageId
   */
  async function loadAnnotations(imageId) {
    imageId = parseInt(imageId);

    if (gImageList.indexOf(imageId) === -1) {
      throw new Error(
          'skipping request to load annotations of image ' + imageId +
          ' as it is not in current image list.');
    }

    let params = {
      image_id: imageId
    };
    let response = await fetch(API_ANNOTATIONS_BASE_URL + 'annotation/load/?' + $.param(params), {
      method: 'GET',
      headers: gHeaders,
    });
    let data = await response.json();
    // save the current annotations
    gCurrentAnnotations = data.annotations;
    globals.currentAnnotationsOfSelectedType = gCurrentAnnotations.filter(function (e) {
      return e.annotation_type.id === gAnnotationType;
    });
    console.log("Fetched annotations for", imageId);
  }

  /**
   * Load the previous or the next image
   *
   * @param offset integer to add to the current image index
   * @return index of the requested image in gImageList
   */
  async function loadAdjacentImage(offset) {
    let imageIndex = gImageList.indexOf(gImageId);
    if (imageIndex < 0) {
      throw new Error('current image is not referenced from page!')
    }

    imageIndex += offset;
    while (imageIndex < 0) {
      imageIndex += imageIndex.length;
    }
    while (imageIndex > imageIndex.length) {
      imageIndex -= imageIndex.length;
    }
    await loadAnnotateView(gImageList[imageIndex]);
  }

  /**
   * Preload next and previous images to cache.
   */
  async function preloadImages() {
    let keepImages = [];
    let cacheLoadings = [];
    for (let imageId = gImageId - PRELOAD_BACKWARD;
         imageId <= gImageId + PRELOAD_FORWARD;
         imageId++) {
      keepImages.push(imageId);
      cacheLoadings.push(loadImageToCache(imageId));
    }
    await Promise.all(cacheLoadings);
    pruneImageCache(keepImages);
  }

  /**
   * Delete all images from cache except for those in Array keep
   *
   * @param keep Array of the image ids which should be kept in the cache.
   */
  function pruneImageCache(keep) {
    for (let imageId in gImageCache) {
      imageId = parseInt(imageId);
      if (gImageCache[imageId] !== undefined && keep.indexOf(imageId) === -1) {
        delete gImageCache[imageId];
      }
    }
  }

  /**
   * Scroll image list to make current image visible.
   */
  function scrollImageList() {
    let imageLink = $('#annotate_image_link_' + gImageId);
    let list = $('#image_list');

    let offset = list.offset().top;
    let linkTop = imageLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  /**
   * Handle the selection change of the annotation type.
   */

  function handleAnnotationTypeChange() {
    gAnnotationType = parseInt($('#annotation_type_id').val());
    globals.currentAnnotationsOfSelectedType = gCurrentAnnotations.filter(function(e) {
      return e.annotation_type.id === gAnnotationType;
    });
    setTool();
    setupCBCheckboxes();
  }

  function handleMouseDown(event) {
    if (!$('#draw_annotations').is(':checked'))
      return;

    let position = globals.image.offset();
    if (event.pageX > position.left && event.pageX < position.left + globals.image.width() &&
            event.pageY > position.top && event.pageY < position.top + globals.image.height())
    {
      if (parseInt($('#annotation_type_id').val()) === -1) {
        displayFeedback($('#feedback_annotation_type_missing'));
        return;
      }
      globals.mouseDownX = Math.round((event.pageX - position.left) * globals.imageScaleWidth);
      globals.mouseDownY = Math.round((event.pageY - position.top) * globals.imageScaleHeight);
      tool.handleMouseDown(event);
    }
  }

  function handleMouseUp(event) {
    if (!$('#draw_annotations').is(':checked'))
      return;

    let position = globals.image.offset();
    globals.mouseUpX = Math.round((event.pageX - position.left)/* * globals.imageScaleWidth*/);
    globals.mouseUpY = Math.round((event.pageY - position.top)/* * globals.imageScaleHeight*/);

    if (event.pageX > position.left && event.pageX < position.left + globals.image.width() &&
      event.pageY > position.top && event.pageY < position.top + globals.image.height()) {
      tool.handleMouseUp(event);
    }
  }

  // handle DEL key press
  async function handleDelete() {
    if (gEditAnnotationId === undefined)
      return;

    await deleteAnnotation(gEditAnnotationId);
  }

  function selectAnnotationType(annotationTypeNumber) {
    let annotationTypeId = '#annotation_type_' + annotationTypeNumber;
    let option = $(annotationTypeId);
    if(option.length) {
      $('#annotation_type_id').val(option.val());
    }
    handleAnnotationTypeChange();
  }


  $(document).ready(function() {
    let get_params = decodeURIComponent(window.location.search.substring(1)).split('&');
    let editAnnotationId = undefined;
    for (let i = 0; i < get_params.length; i++) {
      let parameter = get_params[i].split('=');
      if (parameter[0] === "edit") {
        editAnnotationId = parameter[1];
        break;
      }
    }
    globals.image = $('#image');
    globals.drawAnnotations = $('#draw_annotations').is(':checked');
    gMousepos = $('#mousepos');
    gMousepos.hide();

    // get current environment
    gCsrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
    gImageId = parseInt($('#image_id').html());
    gImageSetId = parseInt($('#image_set_id').html());
    gHeaders = {
      "Content-Type": 'application/json',
      "X-CSRFTOKEN": gCsrfToken
    };
    gImageList = getImageList();
    scrollImageList();
    loadAnnotationTypeList();

    // W3C standards do not define the load event on images, we therefore need to use
    // it from window (this should wait for all external sources including images)
    $(window).on('load', function() {
      setTool();
      tool.initSelection();
      loadAnnotateView(gImageId);
      preloadImages();
    }());

    $('.annotation_value').on('input', function() {
      tool.reloadSelection();
    });
    $('#not_in_image').on('change', handleNotInImageToggle);
    handleNotInImageToggle();
    $('select#filter_annotation_type').on('change', loadImageList);
    $('#filter_update_btn').on('click', loadImageList);
    $('select').on('change', function() {
      document.activeElement.blur();
    });
    $('#draw_annotations').on('change', handleShowAnnotationsToggle);
    $('select#annotation_type_id').on('change', handleAnnotationTypeChange);

    // register click events
    $(window).click(function(e) {
      handleMouseClick(e);
    });
    $('#cancel_edit_button').click(function() {
      resetSelection();
    });
    $('#save_button').click(async function (event) {
      event.preventDefault();
      try {
        let annotation = getValidAnnotation()
        await createAnnotation(annotation);
      } catch (e) {
        console.log(e);
      }
    });
    $('#reset_button').click(function() {
      resetSelection();
    });
    $('#last_button').click(async function (event) {
      try {
        let annotation = getValidAnnotation(true);
        let annotationPromise = createAnnotation(annotation);
        let imagePromise = loadImageList().then(r => {
          return loadAdjacentImage(-1);
        })
        await Promise.all([annotationPromise, imagePromise]);
      } catch (e) {
        console.log(e);
      }
    });
    $('#back_button').click(async function (event) {
      await loadAdjacentImage(-1);
    });
    $('#skip_button').click(async function (event) {
      await loadAdjacentImage(1)
    });
    $('#next_button').click(async function (event) {
      try {
        let annotation = getValidAnnotation(true);
        let annotationPromise = createAnnotation(annotation);
        let imagePromise = loadImageList().then(r => {
          return loadAdjacentImage(1);
        })
        await Promise.all([annotationPromise, imagePromise]);
      } catch (e) {
        console.log(e);
      }
    });
    $('.js_feedback').mouseover(function() {
      $(this).addClass('hidden');
    });
    $('.annotate_image_link').click(async function(event) {
      event.preventDefault(); // do not let the browser load the link
      await loadAnnotateView($(this).data('imageid'));
    });

    // annotation buttons
    $('.annotation_edit_button').each(function(key, elem) {
      elem = $(elem);
      elem.click(function(event) {
        editAnnotation(this, parseInt(elem.data('annotationid')));
      });
    });
    $('.annotation_delete_button').each(function(key, elem) {
      elem = $(elem);
      elem.click(async function(event) {
        event.preventDefault();  // the button is a link, don't follow it
        await deleteAnnotation(parseInt(elem.data('annotationid')));
      });
    });

    $(document).on('mousemove touchmove', handleSelection);
    $(window).on('resize', handleResize);
    window.onpopstate = async function(event) {
      if (event.state !== undefined && event.state !== null && event.state.imageId !== undefined) {
        await loadAnnotateView(event.state.imageId, true);
      }
    };

    // attach listeners for mouse events
    $(document).on('mousedown.annotation_edit', handleMouseDown);
    // we have to bind the mouse up event globally to also catch mouseup on small selections
    $(document).on('mouseup.annotation_edit', handleMouseUp);

    $(document).keydown(function(event) {
      switch (event.keyCode){
        case 16: // Shift
          gShiftDown = true;
          break;
        case 27: // Escape
          if (globals.annotation_type_id === 4) {
            // special case multiline: close drawing
            tool.closeDrawing();
          } else {
            // normally, just delete the selection
            resetSelection();
          }
          break;
        case 73: //i
          if(gShiftDown) {
            tool.increaseSelectionSizeUp();
            break;
          }
          tool.moveSelectionUp();
          break;
        case 75: //k
          if(gShiftDown) {
            tool.decreaseSelectionSizeFromTop();
            break;
          }
          tool.moveSelectionDown();
          break;
        case 76: //l
          if(gShiftDown) {
            tool.increaseSelectionSizeRight();
            break;
          }
          tool.moveSelectionRight();
          break;
        case 74: //j
          if(gShiftDown) {
            tool.decreaseSelectionSizeFromRight();
            break;
          }
          tool.moveSelectionLeft();
          break;
        case 48: //0
          selectAnnotationType(10);
          break;
        case 49: //1
          selectAnnotationType(1);
          break;
        case 50: //2
          selectAnnotationType(2);
          break;
        case 51: //3
          selectAnnotationType(3);
          break;
        case 52: //4
          selectAnnotationType(4);
          break;
        case 53: //5
          selectAnnotationType(5);
          break;
        case 54: //6
          selectAnnotationType(6);
          break;
        case 55: //7
          selectAnnotationType(7);
          break;
        case 56: //8
          selectAnnotationType(8);
          break;
        case 57: //9
          selectAnnotationType(9);
          break;
      }
    });
    $(document).keyup(async function(event) {
      switch (event.keyCode){
        case 16: // Shift
              gShiftDown = false;
              break;
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
          $('#not_in_image').click();
          break;
        case 82: //r
          $('#reset_button').click();
          break;
        case 86: //'v'
          $('#save_button').click();
          break;
        case 46: //'DEL'
          await handleDelete();
          break;
        case 66: //b
          $('#blurred').click();
          break;
        case 67: //c
          $('#concealed').click();
          break;
      }
    });
    $(document).one("ajaxStop", function() {
      selectAnnotationType($('#main_annotation_type_id').html());
      if (editAnnotationId) {
        $('#annotation_edit_button_' + editAnnotationId).click();
      }
    });
  });
})();
