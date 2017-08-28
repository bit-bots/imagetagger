(function() {
  const API_BASE_URL = '/annotations/api/';
  const PRELOAD_BACKWARD = 2;
  const PRELOAD_FORWARD = 5;
  const STATIC_ROOT = '/static/';
  const FEEDBACK_DISPLAY_TIME = 3000;

  // TODO: Find a solution for url resolvings

  var gCsrfToken;
  var gHeaders;
  var gHideFeedbackTimeout;
  var gImage;
  var gImageCache = {};
  var gImageId;
  var gImageList;
  var gImageScale = 0;
  var gInitialized = false;
  var gMousepos;
  var gSelection;

  /**
   * Calculate the correct imageScale value.
   */
  function calculateImageScale() {
    gImageScale = gImage.get(0).naturalWidth / gImage.width();
  }

  /**
   * Create an annotation using the form data from the current page.
   *
   * @param event
   * @param success_callback a function to be executed on success
   */
  function createAnnotation(event, success_callback) {
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
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify({
        annotation_type_id: annotationTypeId,
        image_id: gImageId,
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

        if (typeof(success_callback) === "function") {
          success_callback();
        }
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
    var existingAnnotations = $('#existing_annotations');
    var noAnnotations = $('#no_annotations');

    if (annotations.length === 0) {
      existingAnnotations.addClass('hidden');
      noAnnotations.removeClass('hidden');
      return;
    }

    noAnnotations.addClass('hidden');

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

    existingAnnotations.html(annotationsHtml).removeClass('hidden');
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
   * Get the image list from all .annotate_imagE_link within #image_list.
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
      onSelectChange: updateAnnotationFields
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
    $('#annotate_image_link_' + imageId).addClass('active');

    if (fromHistory !== true) {
      history.pushState({
        imageId: imageId
      }, document.title, '/annotations/' + imageId + '/');
    }

    // Load existing annotations for this image
    var params = {
      image_id: imageId
    };
    $.ajax(API_BASE_URL + 'annotation/load/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function(data) {
        loading.addClass('hidden');
        displayExistingAnnotations(data.annotations);

        resetSelection();
      },
      error: function() {
        loading.addClass('hidden');
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
      'src', '/images/image_nginx/' + imageId + '/');
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
  function resetSelection() {
    $('.annotation_value').val(0);

    if (gSelection !== undefined) {
      gSelection.cancelSelection();
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

    console.log(gImageId);
    console.log(offset);
    console.log(linkTop);
    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  /**
   * Update the contents of the annotation values
   *
   * @param img
   * @param selection
   */
  function updateAnnotationFields(img, selection) {
    $('#x1Field').val(Math.ceil(selection.x1 * gImageScale));
    $('#y1Field').val(Math.ceil(selection.y1 * gImageScale));
    $('#x2Field').val(Math.floor(selection.x2 * gImageScale));
    $('#y2Field').val(Math.floor(selection.y2 * gImageScale));
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
    gImage = $('#image');
    gMousepos = $('#mousepos');
    gMousepos.hide();

    // get current environment
    gCsrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
    gImageId = parseInt($('#image_id').html());
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

    // register click events
    $('#save_button').click(createAnnotation);
    $('#reset_button').click(resetSelection);
    $('#last_button').click(function(event) {
      event.preventDefault();
      createAnnotation(undefined, function() {
        loadAdjacentImage(-1);
      });
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
      });
    });
    $('.js_feedback').click(function() {
      $(this).addClass('hidden');
    });
    $('.annotate_image_link').click(function(event) {
      event.preventDefault();
      loadAnnotateView($(this).data('imageid'));
    });

    $(document).on('mousemove touchmove', handleSelection);
    $(window).on('resize', handleResize);
    window.onpopstate = function(event) {
      if (event.state !== undefined && event.state.imageId !== undefined) {
        loadAnnotateView(event.state.imageId, true);
      }
    };


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
