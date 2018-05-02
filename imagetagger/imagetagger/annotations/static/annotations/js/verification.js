globals = {
  image: undefined,
  imageScaleWidth: undefined,
  imageScaleHeight: undefined
};
(function() {
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
  let gAnnotationId;  // the selected annotation

  function loadAnnotationList(id) {
    // TODO: limit the amount of annotations and load more when needed
    let params = {
      imageset_id: id
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/loadset/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function (data) {
        gAnnotationList = data.annotations;
        gImageSet = getImageSet();
        displayAnnotationList(gAnnotationList);
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
    var annotationLink = $('#annotation_link_' + annotationId);
    var list = $('#annotation_list');

    var offset = list.offset().top;
    var linkTop = annotationLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  function verifyAnnotation(id, state) {
    let strState = 'reject';
    if (state) {
      strState = 'accept';
    }
    var data = {
      annotation_id: id,
      state: strState
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/verify/', {
      type: 'POST',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function (data) {
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
      console.log(
        'skipping request to load image ' + imageId +
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
   * Preload next and previous images to cache.
   */
  function preloadImages() {
    // TODO: preload the next needed images according to the annotations
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
   * Display the annotations of an annotation list.
   *
   * @param annotationList
   */
  function displayAnnotationList(annotationList) {
    var oldAnnotationList = $('#annotation_list');
    var result = $('<div>');
    var annotationContained = false;

    if ($('#filter_verified_checkbox').prop('checked')) {
      annotationList = annotationList.filter(function (annotation) {
          return annotation.verified_by_user;
      });
    }

    result.addClass('panel-body');
    oldAnnotationList.html('');

    for (var i = 0; i < annotationList.length; i++) {
      var annotation = annotationList[i];
      result.append(annotation.image.name + ": ");

      var link = $('<a>');
      link.attr('id', 'annotation_link_' + annotation.id);
      link.attr('href', VERIFY_URL.replace('%s', annotation.id));
      link.addClass('annotation_link');
      if (annotation.id === gAnnotationId) {
        link.addClass('active');
        annotationContained = true;
      }
      let annotation_text_array = [];
      for (let i = 1; i <= Object.keys(annotation.vector).length / 2; i++) {
        annotation_text_array.push("'x" + i + "': " + annotation.vector["x" + i] +
          ", 'y" + i + "': " + annotation.vector["y" + i]);
      }

      link.text("{" + annotation_text_array.join(', ') + "}");
      link.data('annotationid', annotation.id);
      link.click(function(event) {
        event.preventDefault();
        gAnnotationId = $(this).data('annotationid');
        loadAnnotationView(gAnnotationId);
      });

      result.append(link);
      result.append("<br />");
    }

    oldAnnotationList.attr('id', '');
    result.attr('id', 'annotation_list');
    oldAnnotationList.replaceWith(result);

    // load first image if current image is not within image set
    if (!annotationContained) {
      loadAnnotationView(annotationList[0].id); // TODO: right view?
    }

    scrollAnnotationList();
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
   * Load the previous or the next image
   *
   * @param offset integer to add to the current image index
   */
  function loadAdjacentAnnotation(offset) {
    let annotationIndexList = [];
    for (let annotation of gAnnotationList) {
      annotationIndexList.push(annotation.id);
    }
    let annotationIndex = annotationIndexList.indexOf(gAnnotationId);
    if (annotationIndex < 0) {
      console.log('current image is not referenced from page!');
      return;
    }

    annotationIndex += offset;
    while (annotationIndex < 0) {
      annotationIndex = 0;
    }
    while (annotationIndex >= annotationIndexList.length) {
      annotationIndex = annotationIndexList.length - 1;
    }

    loadAnnotationView(annotationIndexList[annotationIndex]);
  }

  /**
   * Load the annotation view for another image.
   *
   * @param imageId
   * @param fromHistory
   */
  function loadAnnotationView(annotationId, fromHistory) {
    gAnnotationId = annotationId;
    let annotation = gAnnotationList.filter(function(e) {
      return e.id === annotationId;
    })[0];
    if (!annotation) {
      console.log(
        'skipping request to load annotation ' + annotationId +
        ' as it is not in current annotation list.');
      return;
    }
    let imageId = annotation.image.id;

    var noAnnotations = $('#no_annotations');
    var notInImage = $('#not_in_image');
    var existingAnnotations = $('#existing_annotations');
    var loading = $('#annotations_loading');
    existingAnnotations.addClass('hidden');
    noAnnotations.addClass('hidden');
    notInImage.prop('checked', false).change();
    loading.removeClass('hidden');

    displayImage(imageId);
    scrollImageList(annotationId);

    $('.annotation_link').removeClass('active');
    var link = $('#annotation_link_' + annotationId);
    link.addClass('active');
    $('#active_image_name').text(link.text());

    if (fromHistory !== true) {
      history.pushState({
        imageId: imageId
      }, document.title, '/annotations/' + annotationId + '/verify/');
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
    return;
    var annotationLink = $('#annotation_link_' + gAnnotationId);
    var list = $('#annotation_list');

    var offset = list.offset().top;
    var linkTop = annotationLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  /**
   * Calculate the correct imageScale value.
   */
  function calculateImageScale() {
    globals.imageScaleWidth = globals.image.get(0).naturalWidth / globals.image.width();
    globals.imageScaleHeight = globals.image.get(0).naturalHeight / globals.image.height();
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
      displayAnnotationList(gAnnotationList);
  }

  $(function() {
    globals.image = $('#picture');
    gAnnotationId = parseInt($('#annotation_id').html());

    let csrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
    gHeaders = {
      "Content-Type": 'application/json',
      "X-CSRFTOKEN": csrfToken
    };

    gImageSetId = parseInt($('#image_set_id').html());

    loadAnnotationList(gImageSetId);

    $('#filter_verified_checkbox').change(function () {
        handleFilterSwitchChange();
    });

    $('#accept_button').click(function () {
      verifyAnnotation(gAnnotationId, true);
      loadAdjacentAnnotation(1);
    });
    $('#reject_button').click(function() {
      verifyAnnotation(gAnnotationId, false);
      loadAdjacentAnnotation(1);
    });
    $('#last_button').click(function(event) {
      loadAdjacentAnnotation(-1);
    });
    $('#edit_button').click(function(event) {
      // TODO: everything
    });
    $('#next_button').click(function(event) {
      loadAdjacentAnnotation(1);
    });
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
      }
    });
  })
})();