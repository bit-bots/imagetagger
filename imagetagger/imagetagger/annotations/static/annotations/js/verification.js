(function() {
  const API_ANNOTATIONS_BASE_URL = '/annotations/api/';
  const FEEDBACK_DISPLAY_TIME = 3000;

  let gHeaders;
  let gHideFeedbackTimeout;

  function loadAnnotationList(id) {
    let params = {
      imageset_id: id
    };
    $.ajax(API_ANNOTATIONS_BASE_URL + 'annotation/loadset/' + $.param(params), {
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

  $(function() {
    let csrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
    gHeaders = {
      "Content-Type": 'application/json',
      "X-CSRFTOKEN": csrfToken
    };
    let imageSetId = parseInt($('#image_set_id').html());
    loadAnnotationList(imageSetId);

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