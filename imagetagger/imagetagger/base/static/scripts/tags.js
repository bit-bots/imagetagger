(function() {
  const API_IMAGES_BASE_URL = '/images/api/imageset/';
  const FEEDBACK_DISPLAY_TIME = 3000;
  const ANNOTATE_URL = '/annotations/%s/';
  const STATIC_ROOT = '/static/';

  // TODO: Find a solution for url resolvings

  var gCsrfToken;
  var gHeaders;
  var gHideFeedbackTimeout;

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

  function addTag() {
    let name = $('#new_tag_name_field').val();

    if (name === '') {
      displayFeedback($('#feedback_empty_tag_name'));
      return;
    }

    let data = {
      tag_name: name,
      image_set_id: gImageSetId
    };

    $('.js_feedback').stop().addClass('hidden');
    $('#add_tag_btn').prop('disabled', true);
    $.ajax(API_IMAGES_BASE_URL + 'tag/', {
      type: 'POST',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function(data, textStatus, jqXHR) {
        if (jqXHR.status === 200) {
          displayFeedback($('#feedback_tag_exists'));
        } else if (jqXHR.status === 201) {
          displayFeedback($('#feedback_tag_created'));
        }
        $('#new_tag_name_field').val('');
        $('#add_tag_btn').prop('disabled', false);
      },
      error: function() {
        $('#add_tag_btn').prop('disabled', false);
        displayFeedback($('#feedback_connection_error'));
      }
    });
  }

  function keypressed(event) {
  let charcode = (event.which) ? event.which : window.event.keyCode;
  // We have to catch Enter here because it would be caught by the outside form
  if (charcode === 13) {
    event.preventDefault();
    return addTag();
  }
  return true;
}

  $(function() {

    // get current environment
    gCsrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
    gImageSetId = parseInt($('#image_set_id').html());
    gHeaders = {
      "Content-Type": 'application/json',
      "X-CSRFTOKEN": gCsrfToken
    };
    $('#add_tag_btn').click(addTag);
    $('#new_tag_name_field').keydown(keypressed);


    $(document).one("ajaxStop", function() {
    });
  });
})();
