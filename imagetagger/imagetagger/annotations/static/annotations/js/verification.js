globals = {
  image: undefined,
  imageScaleWidth: undefined,
  imageScaleHeight: undefined,
  drawAnnotations: true
};

/**
 * Calculate the correct imageScale value.
 */
function calculateImageScale() {
  globals.imageScaleWidth = globals.image.get(0).naturalWidth / globals.image.width();
  globals.imageScaleHeight = globals.image.get(0).naturalHeight / globals.image.height();
}

(function() {
  const EDIT_ANNOTATION_URL = '/annotations/%s/';
  const API_ANNOTATIONS_BASE_URL = '/annotations/api/';
  const FEEDBACK_DISPLAY_TIME = 3000;
  const VERIFY_URL = "/annotations/%s/verify/";
  const PRELOAD_FORWARD = 5;
  const PRELOAD_BACKWARD = 2;

  let gHeaders;
  let gHideFeedbackTimeout;
  let gAnnotationList;
  let gImageId;
  let gImageSet;
  let gImageSetId;
  let gImageCache = {};
  let gAnnotation = {};  // the selected annotation
  let tool;

  function loadFilteredAnnotationList() {
    // TODO: limit the amount of annotations and load more when needed
    let params = {
      imageset_id: gImageSetId,
      verified: $('#filter_verified_checkbox').prop('checked'),
      annotation_type: $('#annotation_type_select').val() || -1
    };
    let link = API_ANNOTATIONS_BASE_URL + 'annotation/loadfilteredset/?' + $.param(params);
    $.ajax(link, {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function (data) {
        gAnnotationList = data.annotations;
        gImageSet = getImageSet();
        displayAnnotationList();
      },
      error: function () {
        displayFeedback($('#feedback_connection_error'))
      }
    })
  }

  function loadAnnotationTypeList() {
    let params = {
      imageset_id: gImageSetId
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/loadsetannotationtypes/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function (data) {
        displayAnnotationTypeOptions(data.annotation_types);
      },
      error: function () {
        displayFeedback($('#feedback_connection_error'))
      }
    })
  }

  /**
   * Scroll image list to make current image visible.
   */
  function scrollImageList(annotationId) {
    let annotationLink = $('#annotation_link_' + annotationId);
    let list = $('#annotation_list');

    let offset = list.offset().top;
    let linkTop = annotationLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  function verifyAnnotation(id, state) {
    let strState = 'reject';
    if (state) {
      strState = 'accept';
    }
    let annotation = gAnnotationList.find(e => e.id === id);
    annotation.verified_by_user = true;
    let data = {
      annotation_id: id,
      state: strState,
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/verify/', {
      type: 'POST',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function () {
        displayFeedback($('#feedback_verify_successful'));
      },
      error: function () {
        displayFeedback($('#feedback_connection_error'));
      }
    })
  }

  /**
   * Display a feedback element for a few seconds.
   *
   * @param elem
   */
  function displayFeedback(elem) {
    $('.js_feedback').stop().addClass('hidden');
    if (gHideFeedbackTimeout !== undefined) {
      clearTimeout(gHideFeedbackTimeout);
    }

    elem.removeClass('hidden');

    gHideFeedbackTimeout = setTimeout(function() {
      $('.js_feedback').addClass('hidden');
    }, FEEDBACK_DISPLAY_TIME);
  }

  /**
   * Load an image to the cache if it is not in it already.
   *
   * @param imageId
   */
  function loadImageToCache(imageId) {
    imageId = parseInt(imageId);

    if (!gImageSet.has(imageId)) {
      // skipping request to load image as it is not in current image list
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
   * Preload next and previous images to cache.
   */
  function preloadImages() {
    // TODO: preload the next needed images according to the annotations
    let keepImages = [];
    for (let imageId = gImageId - PRELOAD_BACKWARD;
         imageId <= gImageId + PRELOAD_FORWARD;
         imageId++) {
      keepImages.push(imageId);
      loadImageToCache(imageId);
    }
    pruneImageCache(keepImages);
  }

  /**
   * Display the annotations of an annotation list.
   *
   * @param annotationList
   */
  function displayAnnotationList() {
    let oldAnnotationList = $('#annotation_list');
    let result = $('<div>');
    let annotationContained = false;

    oldAnnotationList.html('');

    for (let annotation of gAnnotationList) {
      result.append(annotation.image.name + ": ");

      let link = $('<a>');
      link.attr('id', 'annotation_link_' + annotation.id);
      link.attr('href', VERIFY_URL.replace('%s', annotation.id));
      link.addClass('annotation_link');
      if (annotation.id === gAnnotation.id) {
        link.addClass('active');
        annotationContained = true;
      }
      link.text(annotation.annotation_type.name);
      link.data('annotationid', annotation.id);
      link.click(function(event) {
        event.preventDefault();
        let annotationId = $(this).data('annotationid');
        loadAnnotationView(annotationId);
      });

      result.append(link);
      result.append("<br />");
    }

    oldAnnotationList.attr('id', '');
    result.attr('id', 'annotation_list');
    oldAnnotationList.replaceWith(result);

    // load first image if current image is not within image set
    if (!annotationContained) {
      if (gAnnotationList.length < 1) {
        displayFeedback($('#no_annotations_error'));
      } else {
        loadAnnotationView(gAnnotationList[0].id);
        scrollAnnotationList();
      }
    } else {
      loadAnnotationView(gAnnotation.id);
      scrollAnnotationList();
    }
  }

  function displayAnnotationTypeOptions(annotationTypeList) {
    // TODO: empty the options?
    let annotationTypeSelect = $('#annotation_type_select');
    $.each(annotationTypeList, function (key, annotationType) {
      annotationTypeSelect.append($('<option/>', {
        name: annotationType.name,
        value: annotationType.id,
        html: annotationType.name
      }));
    });
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
   * Load the previous or the next image
   *
   * @param offset integer to add to the current image index
   */
  function loadAdjacentAnnotation(offset) {
    let annotationIndex = gAnnotationList.findIndex(e => e.id === gAnnotation.id);
    if (annotationIndex < 0) {
      console.log('current image is not referenced from page!');
      return;
    }
    annotationIndex += offset;
    if (annotationIndex < 0) {
      displayFeedback($('#feedback_last_annotation'));
      return;
    } else if (annotationIndex >= gAnnotationList.length) {
      displayFeedback($('#feedback_last_annotation'));
      return;
    }
    loadAnnotationView(gAnnotationList[annotationIndex].id);
  }

  /**
   * Load the annotation view for another image.
   *
   * @param imageId
   * @param fromHistory
   */
  function loadAnnotationView(annotationId, fromHistory) {
    gAnnotation = gAnnotationList.find(e => e.id === annotationId);
    if (!gAnnotation) {
      // skipping request to load annotation as it is not in current annotation list
      return;
    }
    if (gAnnotation.verified_by_user) {
      displayFeedback($('#feedback_already_verified'));
    }
    let imageId = gAnnotation.image.id;

    let noAnnotations = $('#no_annotations');
    let notInImage = $('#not_in_image');
    let existingAnnotations = $('#existing_annotations');
    let loading = $('#annotations_loading');
    existingAnnotations.addClass('hidden');
    noAnnotations.addClass('hidden');
    notInImage.prop('checked', false).change();
    loading.removeClass('hidden');

    displayImage(imageId);
    scrollImageList(gAnnotation.id);

    $('.annotation_link').removeClass('active');
    let link = $('#annotation_link_' + gAnnotation.id);
    link.addClass('active');
    $('#active_image_name').text(link.text());

    if (fromHistory !== true) {
      history.pushState({
        imageId: imageId
      }, document.title, '/annotations/' + gAnnotation.id + '/verify/');
    }
    $('#annotation-type-title').html('<b>Annotation type: ' + gAnnotation.annotation_type.name + '</b>');
    $('#concealed').prop('checked', gAnnotation.concealed);
    if (gAnnotation.concealed) {
      $('#concealed_label').show()
    } else {
      $('#concealed_label').hide()
    }
    $('#blurred').prop('checked', gAnnotation.blurred);
    if (gAnnotation.blurred) {
      $('#blurred_label').show()
    } else {
      $('#blurred_label').hide()
    }
    drawCurrentAnnotation();
  }

  /**
   * Draw the current annotation that should be verified
   */
  function drawCurrentAnnotation() {
    if (tool) {
      tool.clear();
    }
    let color = '#FF0000';
    if (gAnnotation.concealed) {
      if (gAnnotation.blurred) {
        color = '#5CB85C';
      } else {
        color = '#F0AD4E';
      }
    }
    else if (gAnnotation.blurred) {
      color = '#5BC0DE'
    }
    if (gAnnotation.vector === null) {
      // Not in image
      $('#image_canvas').removeClass('hidden').attr('width', $('#image').width()).attr('height', $('#image').height());
      tool = new Canvas($('#image_canvas'), 3);
      tool.drawCross(color);
      $('#concealed_p').hide();
      $('#blurred_p').hide();
      $('#not_in_image_label').show();
    } else if (!tool || tool.annotationTypeId !== gAnnotation.annotation_type.id ||
      (tool.vector_type === 5 && tool.node_count !== gAnnotation.annotation_type.node_count)) {
      switch (gAnnotation.annotation_type.vector_type) {
        case 1: // Boundingbox
          tool = new BoundingBoxes(gAnnotation.annotation_type.id, true);
          $('#image_canvas').addClass('hidden');
          break;
        case 2: // Point
        case 3: // Line
        case 4: // Multiline
        case 5: // Polygon
          $('#image_canvas').removeClass('hidden').attr('width', $('#image').width()).attr('height', $('#image').height());
          tool = new Canvas($('#image_canvas'), gAnnotation.annotation_type.vector_type,
            gAnnotation.annotation_type.node_count, gAnnotation.annotation_type.id);
          break;
      }
      $('#concealed_p').show();
      $('#blurred_p').show();
      $('#not_in_image_label').hide();
      tool.drawExistingAnnotations([gAnnotation], color);
    } else {
      $('#concealed_p').show();
      $('#blurred_p').show();
      $('#not_in_image_label').hide();
      tool.drawExistingAnnotations([gAnnotation], color);
    }
  }

  /**
   * Display an image from the image cache or the server.
   *
   * @param imageId
   */
  function displayImage(imageId) {
    imageId = parseInt(imageId);

    if (!gImageSet.has(imageId)) {
      console.log(
        'skiping request to load image ' + imageId +
        ' as it is not in current image list.');
      return;
    }

    if (gImageCache[imageId] === undefined) {
      // image is not available in cache. Load it.
      loadImageToCache(imageId);
    }

    // image is in cache.
    let currentImage = globals.image;
    let newImage = gImageCache[imageId];

    currentImage.attr('id', '');
    newImage.attr('id', 'image');
    gImageId = imageId;
    preloadImages();

    currentImage.replaceWith(newImage);
    globals.image = newImage;
    calculateImageScale();

    if (currentImage.data('imageid') !== undefined) {
      // add previous image to cache
      gImageCache[currentImage.data('imageid')] = currentImage;
    }
  }


  /**
   * Scroll image list to make current image visible.
   */
  function scrollAnnotationList() {
    let annotationLink = $('#annotation_link_' + gAnnotation.id);
    let list = $('#annotation_list');

    let offset = list.offset().top;
    let linkTop = annotationLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  /**
   * Get a set of the images in the current imageset.
   */
  function getImageSet() {
    let imageSet = new Set();
    for (let annotation of gAnnotationList) {
      imageSet.add(annotation.image.id);
    }
    return imageSet;
  }

  function handleFilterSwitchChange() {
    loadFilteredAnnotationList(gImageSetId);
  }

  function handleAnnotationTypeSelectChange() {
    loadFilteredAnnotationList(gImageSetId);
  }

  function handleConcealedChange() {
    if (gAnnotation.vector === null) {
      // Not in image
      return;
    }
    gAnnotation.concealed = $('#concealed').is(':checked');
    if (gAnnotation.concealed) {
      $('#concealed_label').show()
    } else {
      $('#concealed_label').hide()
    }
    drawCurrentAnnotation();
    apiBlurredConcealed();
  }

  function handleBlurredChange() {
    if (gAnnotation.vector === null) {
      // Not in image
      return;
    }
    gAnnotation.blurred = $('#blurred').is(':checked');
    if (gAnnotation.blurred) {
      $('#blurred_label').show()
    } else {
      $('#blurred_label').hide()
    }
    drawCurrentAnnotation();
    apiBlurredConcealed();
  }

  function apiBlurredConcealed() {
    let data = {
      annotation_id: gAnnotation.id,
      blurred: gAnnotation.blurred,
      concealed: gAnnotation.concealed
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/blurred_concealed/', {
      method: 'POST',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function() {
        displayFeedback($('#feedback_update_successful'));
      },
      error: function() {
        displayFeedback($('#feedback_connection_error'));
      }
    });
  }

  $(function() {
    globals.image = $('#image');
    gAnnotation.id = parseInt($('#annotation_id').html());

    let csrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
    gHeaders = {
      "Content-Type": 'application/json',
      "X-CSRFTOKEN": csrfToken
    };

    gImageSetId = parseInt($('#image_set_id').html());
    $('#blurred_label').hide();
    $('#concealed_label').hide();
    loadAnnotationTypeList();
    loadFilteredAnnotationList();

    $('#filter_update_btn').on('click', handleFilterSwitchChange);
    $('#filter_verified_checkbox').change(handleFilterSwitchChange);
    $('#annotation_type_select').change(handleAnnotationTypeSelectChange);

    $('#accept_button').click(function () {
      verifyAnnotation(gAnnotation.id, true);
      loadAdjacentAnnotation(1);
    });
    $('#reject_button').click(function() {
      verifyAnnotation(gAnnotation.id, false);
      loadAdjacentAnnotation(1);
    });
    $('#last_button').click(function() {
      loadAdjacentAnnotation(-1);
    });
    $('#edit_button').click(function() {
      parent.location = EDIT_ANNOTATION_URL.replace("%s", gImageId) + '?edit=' + gAnnotation.id;
    });
    $('#next_button').click(function() {
      loadAdjacentAnnotation(1);
    });
    $('#concealed').click(handleConcealedChange);
    $('#blurred').click(handleBlurredChange);
    $('.js_feedback').mouseover(function() {
      $(this).addClass('hidden');
    });

    $(document).keyup(function(event){
      switch(event.keyCode){
        case 68: //d
          $('#next_button').click();
          break;
        case 83: //s
          $('#last_button').click();
          break;
        case 69: //e
          $('#edit_button').click();
          break;
        case 74: //j
          $('#accept_button').click();
          break;
        case 75: //k
          $('#reject_button').click();
          break;
        case 66: //b
          $('#blurred').click();
          break;
        case 67: //c
          $('#concealed').click();
          break;
      }
    });
  })
})();
