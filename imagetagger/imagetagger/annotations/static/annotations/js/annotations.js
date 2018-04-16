(function() {
  const API_ANNOTATIONS_BASE_URL = '/annotations/api/';
  const API_IMAGES_BASE_URL = '/images/api/';
  const FEEDBACK_DISPLAY_TIME = 3000;
  const ANNOTATE_URL = '/annotations/%s/';
  const IMAGE_SET_URL = '/images/imageset/%s/';
  const PRELOAD_BACKWARD = 2;
  const PRELOAD_FORWARD = 5;
  const STATIC_ROOT = '/static/';

  // TODO: Find a solution for url resolvings

  var gCsrfToken;
  var gEditActiveContainer;
  var gEditedAnnotationId;
  var gHeaders;
  var gHideFeedbackTimeout;
  var gImage;
  var gImageCache = {};
  var gImageId;
  var gImageSetId;
  var gImageList;
  var gImageScale = 0;
  var gInitialized = false;
  var gMousepos;
  var gRestoreSelection;
  var gSelection;
  var gMoveSelectionStepsize  = 2;

  var gMouseDownX;
  var gMouseDownY;
  var gMouseUpX;
  var gMouseUpY;
  var gShiftDown;

  // a threshold for editing an annotation if you select a small rectangle
  var gSelectionThreshold = 5;

  // save the current annotations of the image, so we can draw and hide the
  // TODO cache annotations
  var gCurrentAnnotations;

  /**
   * Calculate the correct imageScale value.
   */
  function calculateImageScale() {
    gImageScale = gImage.get(0).naturalWidth / gImage.width();
  }

  /**
   * Create an annotation using the form data from the current page.
   * If an annotation is currently edited, an update is triggered instead.
   *
   * @param event
   * @param successCallback a function to be executed on success
   * @param markForRestore
   */
  function createAnnotation(event, successCallback, markForRestore, reload_list) {
    if (event !== undefined) {
      // triggered using an event handler
      event.preventDefault();
    }

    var annotationTypeId = parseInt($('#annotation_type_id').val());
    var vector = null;

    if (isNaN(annotationTypeId)) {
      displayFeedback($('#feedback_annotation_type_missing'));
      return;
    }

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

    if (markForRestore === true) {
      gRestoreSelection = vector;
    }

    var action = 'create';
    var data = {
      annotation_type_id: annotationTypeId,
      image_id: gImageId,
      vector: vector
    };
    var editing = false;
    if (gEditedAnnotationId !== undefined) {
      // edit instead of create
      action = 'update';
      data.annotation_id = gEditedAnnotationId;
      editing = true;
    }

    $('.js_feedback').stop().addClass('hidden');
    $('.annotate_button').prop('disabled', true);
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/' + action + '/', {
      type: 'POST',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function(data, textStatus, jqXHR) {
        // update current annotations
        gCurrentAnnotations = data.annotations;

        $('.annotate_button').prop('disabled', false);

        if (jqXHR.status === 200) {
          if (editing) {
            if (data.detail === 'similar annotation exists.') {
              displayFeedback($('#feedback_annotation_exists_deleted'));
              $('#annotation_edit_button_' + gEditedAnnotationId).parent().parent(
                ).fadeOut().remove();
            } else {
              displayFeedback($('#feedback_annotation_updated'));
              displayExistingAnnotations(data.annotations);
              if (reload_list === true) {
                  loadImageList();
              }
              drawExistingAnnotations();
            }
          } else {
            displayFeedback($('#feedback_annotation_exists'));
          }
        } else if (jqXHR.status === 201) {
          displayFeedback($('#feedback_annotation_created'));
          displayExistingAnnotations(data.annotations);
          if (reload_list === true) {
              loadImageList();
          }
          drawExistingAnnotations();
        }

        resetSelection(true);

        if (typeof(successCallback) === "function") {
          successCallback();
        }
      },
      error: function() {
        $('.annotate_button').prop('disabled', false);
        displayFeedback($('#feedback_connection_error'));
      }
    });
  }

  /**
   * Delete an annotation.
   *
   * @param event
   * @param annotationId
   */
  function deleteAnnotation(event, annotationId) {
    if (gEditedAnnotationId === annotationId) {
      // stop editing
      resetSelection(true);
      $('#not_in_image').prop('checked', false).change();
    }

    if (event !== undefined) {
      // triggered using an event handler
      event.preventDefault();

      // TODO: Do not use a primitive js confirm
      if (!confirm('Do you really want to delete the annotation?')) {
        return;
      }
    }
    $('.js_feedback').stop().addClass('hidden');
    var params = {
      annotation_id: annotationId
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/delete/?' + $.param(params), {
      type: 'DELETE',
      headers: gHeaders,
      dataType: 'json',
      success: function(data) {
        // remove the annotation from current annotations
        // do not load the annotations from the server again
        for (var annotation in gCurrentAnnotations) {
          var id = gCurrentAnnotations[annotation].id;
          if (id === annotationId) {
            delete gCurrentAnnotations[annotation];
          }
        }
        // redraw the annotations
        drawExistingAnnotations();

        displayFeedback($('#feedback_annotation_deleted'));
        $('#annotation_edit_button_' + annotationId).parent().parent().fadeOut().remove();
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
    var existingAnnotations = $('#existing_annotations');
    var noAnnotations = $('#no_annotations');

    existingAnnotations.addClass('hidden');

    if (annotations.length === 0) {
      noAnnotations.removeClass('hidden');
      return;
    }

    noAnnotations.addClass('hidden');
    existingAnnotations.html('');

    // display new annotations
    for (var i = 0; i < annotations.length; i++) {
      var annotation = annotations[i];

      var alertClass = '';
      if (gEditedAnnotationId === annotation.id) {
        alertClass = ' alert-info';
      }
      var newAnnotation = $(
        '<div id="annotation_' + annotation.id +
        '" class="annotation' + alertClass + '">');

      if (annotation.vector !== null) {
        annotation.content = '';
        for (var key in annotation.vector) {
          if (annotation.content !== '') {
            annotation.content += ' &bull; ';
          }
          annotation.content += '<em>' + key + '</em>: ' + annotation.vector[key];
        }
      }

      newAnnotation.append(annotation.annotation_type.name + ':');

      var annotationLinks = $('<div style="float: right;">');
      var verifyButton = $('<a href="/annotations/' + annotation.id + '/verify/">' +
      '<img src="' + STATIC_ROOT + 'symbols/checkmark.png" alt="verify" class="annotation_verify_button">' +
      '</a>');
      var editButton = $('<a href="/annotations/' + annotation.id + '/edit/">' +
      '<img src="' + STATIC_ROOT + 'symbols/pencil.png" alt="edit" class="annotation_edit_button">' +
      '</a>');
      var deleteButton = $('<a href="/annotations/' + annotation.id + '/delete/">' +
      '<img src="' + STATIC_ROOT + 'symbols/bin.png" alt="delete" class="annotation_delete_button">' +
      '</a>');
      const annotationId = annotation.id;
      editButton.attr('id', 'annotation_edit_button_' + annotationId);
      editButton.click(function(event) {
        editAnnotation(event, this, annotationId);
      });
      editButton.data('annotationtypeid', annotation.annotation_type.id);
      editButton.data('vector', annotation.vector);
      deleteButton.click(function(event) {
        deleteAnnotation(event, annotationId);
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

  function drawExistingAnnotations() {
    clearBoundingBoxes();
    calculateImageScale();

    if (gCurrentAnnotations.length === 0 || !$('#draw_annotations').prop('checked')) {
        return;
    }

    // clear all boxes
    var boundingBoxes = document.getElementById('boundingBoxes');

    var annotationType = parseInt($('#annotation_type_id').val());

    for (var a in gCurrentAnnotations) {

      var annotation = gCurrentAnnotations[a];
      if (annotation.annotation_type.id !== annotationType) {
        continue;
      }
      if (annotation.vector === null) {
          continue;
      }

      var boundingBox = document.createElement('div');
      boundingBox.setAttribute('id', 'boundingBox');
      $(boundingBox).css({
          'top': annotation.vector.y1/gImageScale,
          'left': annotation.vector.x1/gImageScale + parseFloat($('img#image').parent().css('padding-left')),
          'width': (annotation.vector.x2 - annotation.vector.x1)/gImageScale,
          'height': (annotation.vector.y2 - annotation.vector.y1)/gImageScale});

      boundingBoxes.appendChild(boundingBox);
    }
  }

  function clearBoundingBoxes() {
    var boundingBoxes = document.getElementById('boundingBoxes');

    while (boundingBoxes.firstChild) {
      boundingBoxes.removeChild(boundingBoxes.firstChild);
    }
  }

  /**
   * Display an image from the image cache or the server.
   *
   * @param imageId
   */
  function displayImage(imageId) {
    imageId = parseInt(imageId);

    if (gImageList.indexOf(imageId) === -1) {
      console.log(
        'skiping request to load image ' + imageId +
        ' as it is not in current image list.');
      return;
    }
    resetSelection();

    if (gImageCache[imageId] === undefined) {
      // image is not available in cache. Load it.
      loadImageToCache(imageId);
    }

    // image is in cache.
    var currentImage = gImage;
    var newImage = gImageCache[imageId];

    currentImage.attr('id', '');
    newImage.attr('id', 'image');
    gImageId = imageId;
    preloadImages();

    currentImage.replaceWith(newImage);
    gImage = newImage;
    initSelection();
    resetSelection();

    if (currentImage.data('imageid') !== undefined) {
      // add previous image to cache
      gImageCache[currentImage.data('imageid')] = currentImage;
    }

    // reattach listeners for mouse events
    $('img').on('mousedown.annotation_edit', handleMouseDown);
    $('img').on('mouseup.annotation_edit', handleMouseUp);
    // we have to bind the mouse up event globally to also catch mouseup on small selections
    $(document).on('mouseup.annotation_edit', handleMouseUp);
  }

  /**
   * Display the images of an image list.
   *
   * @param imageList
   */
  function displayImageList(imageList) {
    var oldImageList = $('#image_list');
    var result = $('<div>');
    var imageContained = false;

    result.addClass('panel-body');
    oldImageList.html('');

    for (var i = 0; i < imageList.length; i++) {
      var image = imageList[i];

      var link = $('<a>');
      link.attr('id', 'annotate_image_link_' + image.id);
      link.attr('href', ANNOTATE_URL.replace('%s', image.id));
      link.addClass('annotate_image_link');
      if (image.id === gImageId) {
        link.addClass('active');
        imageContained = true;
      }
      link.text(image.name);
      link.data('imageid', image.id);
      link.click(function(event) {
        event.preventDefault();
        loadAnnotateView($(this).data('imageid'));
      });

      result.append(link);
    }

    oldImageList.attr('id', '');
    result.attr('id', 'image_list');
    oldImageList.replaceWith(result);

    gImageList = getImageList();

    // load first image if current image is not within image set
    if (!imageContained) {
      loadAnnotateView(imageList[0].id);
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
   * @param event
   * @param annotationElem the element which stores the edit button of the annotation
   * @param annotationId
   */
  function editAnnotation(event, annotationElem, annotationId) {
    annotationElem = $(annotationElem);

    gEditedAnnotationId = annotationId;
    gEditActiveContainer.removeClass('hidden');

    resetSelection();

    if (event !== undefined) {
      // triggered using an event handler
      event.preventDefault();
    }
    $('.js_feedback').stop().addClass('hidden');
    var params = {
      annotation_id: annotationId
    };

    var annotationData = annotationElem.data('vector');
    if (annotationData === undefined) {
      annotationData = annotationElem.data('escapedvector');
    }
    var annotationTypeId = annotationElem.data('annotationtypeid');

    // highlight currently edited annotation
    $('.annotation').removeClass('alert-info');
    annotationElem.parent().parent().addClass('alert-info');

    var notInImage = $('#not_in_image');
    if (annotationData === null) {
      // not in image
      notInImage.prop('checked', true).change();
      return;
    }

    notInImage.prop('checked', false).change();

    $('#annotation_type_id').val(annotationTypeId);
    $('#x1Field').val(annotationData.x1);
    $('#x2Field').val(annotationData.x2);
    $('#y1Field').val(annotationData.y1);
    $('#y2Field').val(annotationData.y2);
    initSelection();

    reloadSelection();
  }

  /**
   * Get the image list from all .annotate_image_link within #image_list.
   */
  function getImageList() {
    var imageList = [];
    $('#image_list').find('.annotate_image_link').each(function(key, elem) {
      var imageId = parseInt($(elem).data('imageid'));
      if (imageList.indexOf(imageId) === -1) {
        imageList.push(imageId);
      }
    });

    return imageList;
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
   * Handle toggle of the draw annotations checkbox.
   *
   * @param event
   */
  function handleShowAnnotationsToggle(event) {
    if ($('#draw_annotations').is(':checked')) {
      drawExistingAnnotations();
    } else {
      clearBoundingBoxes();
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
    var position = gImage.offset();
    if (event.pageX > position.left &&
          event.pageX < position.left + gImage.width() &&
          event.pageY > position.top &&
          event.pageY < position.top + gImage.height()) {
      cH.show();
      cV.show();
      gMousepos.show();

      cH.css('top', event.pageY + 1);
      cV.css('left', event.pageX + 1);
      cV.css('height', gImage.height() - 1);
      cV.css('margin-top', position.top);
      cH.css('width', gImage.width() - 1);
      cH.css('margin-left', position.left);

      gMousepos.css({
        top: (event.pageY) + 'px',
        left: (event.pageX)  + 'px'
      }, 800);
      gMousepos.text(
        '(' + Math.round((event.pageX - position.left) * gImageScale) + ', ' +
        Math.round((event.pageY - position.top) * gImageScale) + ')');
      event.stopPropagation();
    }
    else{
      cH.hide();
      cV.hide();
      gMousepos.hide();
    }
  }

  /**
   * Handle a resize event of the window.
   *
   * @param event
   */
  function handleResize() {
    gSelection.cancelSelection();
    calculateImageScale();
    drawExistingAnnotations();
  }

  /**
   * Initialize the selection.
   */
  function initSelection() {
    gInitialized = true;

    gSelection = gImage.imgAreaSelect({
      instance: true,
      show: true,
      minHeight: 2,
      minWidth: 2,
      onSelectChange: updateAnnotationFields,
      resizeMargin: 3
    });
    gSelection.cancelSelection();
  }

  /**
   * Load the annotation view for another image.
   *
   * @param imageId
   * @param fromHistory
   */
  function loadAnnotateView(imageId, fromHistory) {
    gEditedAnnotationId = undefined;

    imageId = parseInt(imageId);

    if (gImageList.indexOf(imageId) === -1) {
      console.log(
        'skiping request to load image ' + imageId +
        ' as it is not in current image list.');
      return;
    }

    var noAnnotations = $('#no_annotations');
    var notInImage = $('#not_in_image');
    var existingAnnotations = $('#existing_annotations');
    var loading = $('#annotations_loading');
    existingAnnotations.addClass('hidden');
    noAnnotations.addClass('hidden');
    notInImage.prop('checked', false).change();
    loading.removeClass('hidden');

    displayImage(imageId);
    scrollImageList();

    $('.annotate_image_link').removeClass('active');
    var link = $('#annotate_image_link_' + imageId);
    link.addClass('active');
    $('#active_image_name').text(link.text());
    restoreSelection(false);

    if (fromHistory !== true) {
      history.pushState({
        imageId: imageId
      }, document.title, '/annotations/' + imageId + '/');
    }

    // load existing annotations for this image
    var params = {
      image_id: imageId
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/load/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function(data) {
        // save the current annotations
        gCurrentAnnotations = data.annotations;
        loading.addClass('hidden');
        displayExistingAnnotations(data.annotations);
        drawExistingAnnotations();

        if (gRestoreSelection !== undefined) {
          restoreSelection();
        } else {
          resetSelection(true);
        }
      },
      error: function() {
        loading.addClass('hidden');
        $('.annotate_button').prop('disabled', false);
        displayFeedback($('#feedback_connection_error'));
      }
    });
  }

  /**
   * Load the image list from tye server applying a new filter.
   */
  function loadImageList() {
    var filterElem = $('#filter_annotation_type');
    var filter = filterElem.val();
    var params = {
      image_set_id: gImageSetId
    };

    if (filter !== '' && !isNaN(filter)) {
      params.filter_annotation_type_id = filter;
      $('#annotation_type_id').val(filter);
    }

    $.ajax(API_IMAGES_BASE_URL + 'imageset/load/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        if (data.image_set.images.length === 0) {
          // redirect to image set view.
          displayFeedback($('#feedback_image_set_empty'));
          filterElem.val('').change();
          return;
        }
        displayImageList(data.image_set.images);
      },
      error: function() {
        $('.annotate_button').prop('disabled', false);
        displayFeedback($('#feedback_connection_error'));
      }
    });
  }

  /**
   * Load an image to the cache if it is not in it already.
   *
   * @param imageId
   */
  function loadImageToCache(imageId) {
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
   * Load the previous or the next image
   *
   * @param offset integer to add to the current image index
   */
  function loadAdjacentImage(offset) {
    var imageIndex = gImageList.indexOf(gImageId);
    if (imageIndex < 0) {
      console.log('current image is not referenced from page!');
      return;
    }

    imageIndex += offset;
    while (imageIndex < 0) {
      imageIndex += imageIndex.length;
    }
    while (imageIndex > imageIndex.length) {
      imageIndex -= imageIndex.length;
    }

    loadAnnotateView(gImageList[imageIndex]);
  }

  /**
   * Preload next and previous images to cache.
   */
  function preloadImages() {
    var keepImages = [];
    for (var imageId = gImageId - PRELOAD_BACKWARD;
         imageId <= gImageId + PRELOAD_FORWARD;
         imageId++) {
      keepImages.push(imageId);
      loadImageToCache(imageId);
    }
    pruneImageCache(keepImages);
  }

  /**
   * Delete all images from cache except for those in Array keep
   *
   * @param keep Array of the image ids which should be kept in the cache.
   */
  function pruneImageCache(keep) {
    for (var imageId in gImageCache) {
      imageId = parseInt(imageId);
      if (gImageCache[imageId] !== undefined && keep.indexOf(imageId) === -1) {
        delete gImageCache[imageId];
      }
    }
  }

  /**
   * Reload the selection.
   */
  function reloadSelection() {
    gSelection = gImage.imgAreaSelect({
      instance: true,
      show: true
    });
    gSelection.setSelection(
      Math.round($('#x1Field').val() / gImageScale),
      Math.round($('#y1Field').val() / gImageScale),
      Math.round($('#x2Field').val() / gImageScale),
      Math.round($('#y2Field').val() / gImageScale)
    );
    gSelection.update();
  }

  /**
   * Delete current selection.
   */
  function resetSelection(abortEdit) {
    $('.annotation_value').val(0);

    if (gSelection !== undefined) {
      gSelection.cancelSelection();
    }

    if (abortEdit === true) {
      gEditedAnnotationId = undefined;
      $('.annotation').removeClass('alert-info');
      gEditActiveContainer.addClass('hidden');
    }
  }

  /**
   * Restore the selection.
   */
  function restoreSelection(reset) {
    if (!$('#keep_selection').prop('checked')) {
      return;
    }
    if (gRestoreSelection !== undefined) {
      if (gRestoreSelection === null) {
        $('#not_in_image').prop('checked', true);
        $('#coordinate_table').hide();
      } else {
        $('#x1Field').val(gRestoreSelection.x1);
        $('#x2Field').val(gRestoreSelection.x2);
        $('#y1Field').val(gRestoreSelection.y1);
        $('#y2Field').val(gRestoreSelection.y2);
        reloadSelection();
      }
    }
    if (reset !== false) {
      gRestoreSelection = undefined;
    }
  }

  /**
   * Scroll image list to make current image visible.
   */
  function scrollImageList() {
    var imageLink = $('#annotate_image_link_' + gImageId);
    var list = $('#image_list');

    var offset = list.offset().top;
    var linkTop = imageLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  /**
   * Update the contents of the annotation values
   *
   * @param img
   * @param selection
   */
  function updateAnnotationFields(img, selection) {
    $('#x1Field').val(Math.round(selection.x1 * gImageScale));
    $('#y1Field').val(Math.round(selection.y1 * gImageScale));
    $('#x2Field').val(Math.round(selection.x2 * gImageScale));
    $('#y2Field').val(Math.round(selection.y2 * gImageScale));
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

  /**
   * Handle the selection change of the annotation type.
   */

  function handleAnnotationTypeChange() {
    var annotationTypeId = parseInt($('#annotation_type_id').val());

    var params = {
      image_id: gImageId
    };

    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/load/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function(data) {
        gCurrentAnnotations = data.annotations;
        drawExistingAnnotations();
      },
      error: function() {
      }
    });
  }

  function handleMouseDown(event) {
    if (!$('#draw_annotations').is(':checked'))
      return;

    var position = gImage.offset();
    if (event.pageX > position.left && event.pageX < position.left + gImage.width() &&
            event.pageY > position.top && event.pageY < position.top + gImage.height())
    {
      gMouseDownX = Math.round((event.pageX - position.left) * gImageScale);
      gMouseDownY = Math.round((event.pageY - position.top) * gImageScale);
    }
  }

  function handleMouseUp(event) {
    if (!$('#draw_annotations').is(':checked'))
      return;

    var position = gImage.offset();
    if (event.pageX > position.left && event.pageX < position.left + gImage.width() &&
            event.pageY > position.top && event.pageY < position.top + gImage.height())
    {
      gMouseUpX = Math.round((event.pageX - position.left) * gImageScale);
      gMouseUpY = Math.round((event.pageY - position.top) * gImageScale);

      // check if we have a click or a small selection
      if (Math.abs(gMouseDownX - gMouseUpX) <= gSelectionThreshold &&
          Math.abs(gMouseDownY - gMouseUpY) <= gSelectionThreshold)
      {
        // get current annotation type id
        var annotationType = parseInt($('#annotation_type_id').val());

        // array with all matching annotations
        var matchingAnnotations = [];

        for (var a in gCurrentAnnotations)
        {
          var annotation = gCurrentAnnotations[a];
          if (annotation.annotation_type.id !== annotationType)
            continue;
          if (annotation.vector === null)
            continue;

          var left = annotation.vector.x1;
          var right = annotation.vector.x2;
          var top = annotation.vector.y1;
          var bottom = annotation.vector.y2;

          // check if we clicked inside that annotation
          if (gMouseDownX >= left && gMouseDownX <= right && gMouseDownY >= top && gMouseDownY <= bottom)
          {
            matchingAnnotations.push(annotation);
          }
        }

        // no matches
        if (matchingAnnotations.length === 0)
          return;

        annotation = matchingAnnotations[0];

        // a single match
        if (matchingAnnotations.length === 1)
        {
           // get the id of the corresponding edit button
          edit_button_id = '#annotation_edit_button_' + annotation.id;
           // trigger click event
          $(edit_button_id).click();
        }
        // multiple matches
        else
        {
          // if we have multiple matching annotations, we have the following descending criteria:
          // 1. prefer annotation lying inside another one completely
          // 2. prefer annotation, which left border is to the left of another ones
          // 3. prefer annotation, which top border is above another ones
          for (var a1 in matchingAnnotations)
          {
            var annotation1 = matchingAnnotations[a1];

            if (annotation.id === annotation1.id)
              continue;

            if (inside(annotation1, annotation))
            {
              annotation = annotation1;
              continue;
            }

            if (inside(annotation, annotation1))
            {
              continue;
            }

            if (leftOf(annotation1, annotation))
            {
              annotation = annotation1;
              continue;
            }

            if (leftOf(annotation, annotation1))
            {
              continue;
            }

            if (above(annotation1, annotation))
            {
              annotation = annotation1;
              continue;
            }

            if (above(annotation, annotation1))
            {
              continue;
            }
          }
          // get the id of the corresponding edit button
          edit_button_id = '#annotation_edit_button_' + annotation.id;
          // trigger click event
          $(edit_button_id).click();
        }
      }
     }
  }

  // checks if annotation a1 is inside annotation a2
  function inside(a1, a2) {
    return a1.vector.x1 >= a2.vector.x1 && a1.vector.y1 >= a2.vector.y1 &&
           a1.vector.x2 <= a2.vector.x2 && a1.vector.y2 <= a2.vector.y2;
  }

  // checks if the left border of annotation a1 is to the left of the left border of annotation a2
  function leftOf(a1, a2) {
    return a1.vector.x1 < a2.vector.x1;
  }

  // checks if the top border of annotation a1 is above the top border of annotation a2
  function above(a1, a2) {
    return a1.vector.y1 < a2.vector.y1;
  }

  // handle DEL key press
  function handleDelete(event) {
    if (gEditedAnnotationId === undefined)
      return;

    deleteAnnotation(event, gEditedAnnotationId);
  }
  function moveSelectionUp() {
    y1 = $('#y1Field').val();
    y2 = $('#y2Field').val();
    // calculate value +/- stepsize (times stepsize to account for differing image sizes)
    newValueY1 = Math.round(parseInt($('#y1Field').val()) - Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    newValueY2 = Math.round(parseInt($('#y2Field').val()) - Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0){
      newValueY1 = 0;
      newValueY2 = $('#y2Field').val(); }
    if (newValueY2 > Math.round(gImage.height()*gImageScale)){
      newValueY2 = Math.ceil(gImage.height()*gImageScale);
      newValueY1 =  $('#y1Field').val();
       }
    // update values
    $('#y1Field').val(newValueY1);
    $('#y2Field').val(newValueY2);
    reloadSelection();
  }
  function moveSelectionDown() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    newValueY1 = Math.round(parseInt($('#y1Field').val()) + Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    newValueY2 = Math.round(parseInt($('#y2Field').val()) + Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0){
      newValueY1 = 0;
      newValueY2 = $('#y2Field').val(); }
    if (newValueY2 > Math.round(gImage.height()*gImageScale)){
      newValueY2 = Math.ceil(gImage.height()*gImageScale);
      newValueY1 =  $('#y1Field').val();
       }
    // update values
    $('#y1Field').val(newValueY1);
    $('#y2Field').val(newValueY2);
    reloadSelection();
  }

  function moveSelectionRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    newValueX1 = Math.round(parseInt($('#x1Field').val()) + Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    newValueX2 = Math.round(parseInt($('#x2Field').val()) + Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0){
      newValueX1 = 0;
      newValueX2 = $('#x2Field').val(); }
    if (newValueX2 > Math.round(gImage.width()*gImageScale)){
      newValueX2 = Math.ceil(gImage.width()*gImageScale);
      newValueX1 =  $('#x1Field').val();
       }
    // update values
    $('#x1Field').val(newValueX1);
    $('#x2Field').val(newValueX2);
    reloadSelection();
  }
  function moveSelectionLeft() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    newValueX1 = Math.round(parseInt($('#x1Field').val()) - Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    newValueX2 = Math.round(parseInt($('#x2Field').val()) - Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0){
      newValueX1 = 0;
      newValueX2 = $('#x2Field').val(); }
    if (newValueX2 > Math.round(gImage.width()*gImageScale)){
      newValueX2 = Math.ceil(gImage.width()*gImageScale);
      newValueX1 =  $('#x1Field').val();
       }
    // update values
    $('#x1Field').val(newValueX1);
    $('#x2Field').val(newValueX2);
    reloadSelection();
  }
  function increaseSelectionSizeUp() {
    y1 = $('#y1Field').val();
    // calculate value +/- stepsize (times stepsize to account for differing image sizes)
    newValueY1 = Math.round(parseInt($('#y1Field').val()) - Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY1 < 0){
      newValueY1 = 0;
    }

    // update values
    $('#y1Field').val(newValueY1);
    reloadSelection();
  }
  function decreaseSelectionSizeDown() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    newValueY1 = Math.round(parseInt($('#y1Field').val()));
    newValueY2 = Math.round(parseInt($('#y2Field').val()) - Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueY2 < 0){
      newValueY2 = 1;
       }
    if (newValueY2 <= newValueY1) {
      newValueY2 = newValueY1 + Math.round(Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    }
    // update values
    $('#y2Field').val(newValueY2);
    reloadSelection();
  }
  function increaseSelectionSizeRight() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    newValueX2 = Math.round(parseInt($('#x2Field').val()) + Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension

    if (newValueX2 > Math.round(gImage.width()*gImageScale)){
      newValueX2 = Math.ceil(gImage.width()*gImageScale);
       }
    // update values
    $('#x2Field').val(newValueX2);
    reloadSelection();
  }
  function decreaseSelectionSizeLeft() {
    // calculate value +/- stepsize times stepsize to account for differing image sizes
    newValueX1 = Math.round(parseInt($('#x1Field').val()) + Math.max(1,(gMoveSelectionStepsize * gImageScale)));
    newValueX2 = Math.round(parseInt($('#x2Field').val()));
    // checking if the box would be out of bounds and puts it to max/min size and doesn't move the other dimension
    if (newValueX1 < 0) {
        newValueX1 = 0;
    }
    if (newValueX1 >= newValueX2){
      newValueX1 = newValueX2 - 1;
    }
    // update values
    $('#x1Field').val(newValueX1);
    reloadSelection();
  }

  function selectAnnotationType(annotationTypeNumber) {
    var annotationTypeId = '#annotation_type_' + annotationTypeNumber;
    var option = $(annotationTypeId);
    if(option.length) {
      $('#annotation_type_id').val(option.val());
    }
  }


  $(function() {
    gEditActiveContainer = $('#edit_active');
    gImage = $('#image');
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
    preloadImages();
    scrollImageList();

    // W3C standards do not define the load event on images, we therefore need to use
    // it from window (this should wait for all external sources including images)
    $(window).on('load', initSelection);

    // TODO: Make this as well as the load handler part of initSelection
    setTimeout(function() {
      // Fallback if window load initialization did not succeed
      if (!gInitialized) {
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
    $('select#filter_annotation_type').on('change', loadImageList);
    $('select').on('change', function() {
      document.activeElement.blur();
    });
    $('#draw_annotations').on('change', handleShowAnnotationsToggle);
    $('select#annotation_type_id').on('change', handleAnnotationTypeChange);

    // register click events
    $('#cancel_edit_button').click(function() {
      resetSelection(true);
    });
    $('#save_button').click(createAnnotation);
    $('#reset_button').click(function() {
      resetSelection(true);
    });
    $('#last_button').click(function(event) {
      event.preventDefault();
      createAnnotation(undefined, function() {
        loadAdjacentImage(-1);
      }, true, true);
    });
    $('#back_button').click(function(event) {
      event.preventDefault();
      loadAdjacentImage(-1);
    });
    $('#skip_button').click(function(event) {
      event.preventDefault();
      loadAdjacentImage(1);
    });
    $('#next_button').click(function(event) {
      event.preventDefault();
      createAnnotation(undefined, function() {
        loadAdjacentImage(1);
      }, true, true);
    });
    $('.js_feedback').mouseover(function() {
      $(this).addClass('hidden');
    });
    $('.annotate_image_link').click(function(event) {
      event.preventDefault();
      loadAnnotateView($(this).data('imageid'));
    });

    // annotation buttons
    $('.annotation_edit_button').each(function(key, elem) {
      elem = $(elem);
      elem.click(function(event) {
        editAnnotation(event, this, parseInt(elem.data('annotationid')));
      });
    });
    $('.annotation_delete_button').each(function(key, elem) {
      elem = $(elem);
      elem.click(function(event) {
        deleteAnnotation(event, parseInt(elem.data('annotationid')));
      });
    });

    $(document).on('mousemove touchmove', handleSelection);
    $(window).on('resize', handleResize);
    window.onpopstate = function(event) {
      if (event.state !== undefined && event.state.imageId !== undefined) {
        loadAnnotateView(event.state.imageId, true);
      }
    };

    // attach listeners for mouse events
    $('img').on('mousedown.annotation_edit', handleMouseDown);
    $('img').on('mouseup.annotation_edit', handleMouseUp);
    // we have to bind the mouse up event globally to also catch mouseup on small selections
    $(document).on('mouseup.annotation_edit', handleMouseUp);

    $(document).keydown(function(event) {
      switch (event.keyCode){
        case 16: // Shift
          gShiftDown = true;
          break;
        case 73: //i
          if(gShiftDown) {
            increaseSelectionSizeUp();
            break;
          }
          moveSelectionUp();
          break;
        case 75: //k
          if(gShiftDown) {
            decreaseSelectionSizeDown();
            break;
          }
          moveSelectionDown();
          break;
        case 76: //l
          if(gShiftDown) {
            increaseSelectionSizeRight();
            break;
          }
          moveSelectionRight();
          break;
        case 74: //j
          if(gShiftDown) {
            decreaseSelectionSizeLeft();
            break;
          }
          moveSelectionLeft();
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
      }})
    // TODO: this should be done only for the annotate view
    $(document).keyup(function(event) {
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
          var notInImage = $('#not_in_image');
          notInImage.prop('checked', !notInImage.is(':checked')).change();
          break;
        case 82: //r
          $('#reset_button').click();
          break;
        case 86: //'v'
          $('#save_button').click();
          break;
        case 46: //'DEL'
          handleDelete(event);
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
