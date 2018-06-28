(function() {
  const API_IMAGES_BASE_URL = '/images/api/imageset/';
  const FEEDBACK_DISPLAY_TIME = 3000;

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
    $.ajax(API_IMAGES_BASE_URL + 'tag/add/', {
      type: 'POST',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function(data, textStatus, jqXHR) {
        if (jqXHR.status === 200) {
          displayFeedback($('#feedback_tag_exists'));
        } else if (jqXHR.status === 201) {
          displayFeedback($('#feedback_tag_created'));
          let inner_span = $('<span class="glyphicon glyphicon-remove-sign tag-delete"></span>');
          inner_span.click(deleteTag);
          let outer_span = $('<span class="label label-info">' + data.tag.name + '&nbsp;</span>');
          inner_span.appendTo(outer_span);
          outer_span.appendTo($('#tags-with-delete'));
          document.getElementById('tags-with-delete').innerHTML += '&#8203;';
          $('<span class="label label-info">' + data.tag.name + '</span>').appendTo($('#tags-without-delete'));
          document.getElementById('tags-without-delete').innerHTML += '&#8203;';
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

  function deleteTag(event) {
    let name = $(this).parent().text().trim();
    let data = {
      tag_name: name,
      image_set_id: gImageSetId
    };
    let self = $(this);
    $.ajax(API_IMAGES_BASE_URL + 'tag/delete/', {
      type: 'DELETE',
      headers: gHeaders,
      dataType: 'json',
      data: JSON.stringify(data),
      success: function(data, textStatus,jqXHR) {
        self.parent().remove();
        $('#tags-without-delete').children().filter(function(number, element) {
          return element.textContent.trim() === name;
        }).remove();
        displayFeedback($('#feedback_tag_removed'));
      },
      error: function() {
        displayFeedback($('#feedback_connection_error'));
      }
    });
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

    $.each($('.tag-delete'), function(number, element) {
      $(element).click(deleteTag);
    });

    $('#new_tag_name_field').autocomplete({
      serviceUrl: API_IMAGES_BASE_URL + 'tag/autocomplete/'
      //appendTo: $('#autocomplete-tags')
    });
  });
})();
