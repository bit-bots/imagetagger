(function() {
  const API_ANNOTATIONS_BASE_URL = '/annotations/api/';
  const FEEDBACK_DISPLAY_TIME = 3000;

  let csrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
  let gHeaders;
  gHeaders = {
    "Content-Type": 'application/json',
    "X-CSRFTOKEN": csrfToken
  };
  let gHideFeedbackTimeout;
  let gAnnotationList;
  let gImageSetId = parseInt($('#image_set_id').html());
  let gImageCache;
  let gAnnotationId;  // the selected annotation

  function loadAnnotationList(id) {
    // TODO: limit the amount of annotations and load more when needed
    var params = {
      imageset_id: id
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/loadset/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function (data) {
        console.log(data)
      },
      error: function () {
        displayFeedback($('#feedback_connection_error'))
      }
    })
  }

  function verifyAnnotation(id, state) {
    let strState = 'reject';
    if (state) {
      strState = 'accept';
    }
    var params = {
      annotation_id: id,
      state: strState
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/verify/?' + $.param(params), {
      type: 'GET',
      headers: gHeaders,
      dataType: 'json',
      success: function (data) {
        console.log(data)
      },
      error: function () {
        displayFeedback($('#feedback_connection_error'))
      }
    })
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
   * Load an image to the cache if it is not in it already.
   *
   * @param imageId
   */
  function loadImageToCache(imageId) {
    imageId = parseInt(imageId);

    // TODO: whatever
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

    if ($('#checkbox').prop('checked')) {
      annotationList.filter(function (annotation) {
          return annotation.verified_by_user;
      });
    }

    result.addClass('panel-body');
    oldAnnotationList.html('');

    for (var i = 0; i < annotationList.length; i++) {
      var annotation = annotationList[i];

      var link = $('<a>');
      link.attr('id', 'annotation_link_' + annotation.id);
      link.attr('href', VERIFY_URL.replace('%s', annotation.id));  // TODO: Set VERIFY URL
      link.addClass('annotation_link');
      if (annotation.id === gAnnotationId) {
        link.addClass('active');
        annotationContained = true;
      }
      link.text(annotation.vector);  // TODO: shorten vector
      link.data('annotationid', annotation.id);
      link.click(function(event) {
        event.preventDefault();
        loadAnnotateView($(this).data('annotationid'));
      });

      result.append(link);
    }

    oldAnnotationList.attr('id', '');
    result.attr('id', 'annotation_list');
    oldAnnotationList.replaceWith(result);

    gImageList = getImageList();  // TODO: This in right

    // load first image if current image is not within image set
    if (!annotationContained) {
      loadAnnotateView(annotationList[0].id); // TODO: right view?
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
   * Scroll image list to make current image visible.
   */
  function scrollAnnotationList() {
    var imageLink = $('#annotate_image_link_' + gImageId);
    var list = $('#annotation_list');

    var offset = list.offset().top;
    var linkTop = imageLink.offset().top;

    // link should be (roughly) in the middle of the element
    offset += parseInt(list.height() / 2);

    list.scrollTop(list.scrollTop() + linkTop - offset);
  }

  function handleFilterSwitchChange() {
      displayAnnotationList();
    }

  $(function() {

    loadAnnotationList(gImageSetId);

    $('#filter_verified_checkbox').change(function () {
        handleFilterSwitchChange();
    });

    $(document).keyup(function(event){
      switch(event.keyCode){
        case 70: //f
          $('#next_unverified_button').click();
          break;
        case 68: //d
          $('#next_button').click();
          break;
        case 83: //s
          $('#last_button').click();
          break;
        case 65: //a
          $('#last_unverified_button').click();
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