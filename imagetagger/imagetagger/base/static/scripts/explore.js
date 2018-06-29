let csrfToken = $('[name="csrfmiddlewaretoken"]').first().val();
let headers = {
  "Content-Type": 'application/json',
  "X-CSRFTOKEN": csrfToken
};

$('#tagbox').autocomplete({
  lookup: function(query, done) {
    let query_array = query.split(',').map(function(element) {
      return element.trim();
    });
    let params = {
      query: query_array[query_array.length - 1]
    };
    $.ajax('/images/api/imageset/tag/autocomplete/?' + $.param(params), {
      type: 'GET',
      headers: headers,
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        query_array.pop();
        let output_string = '';
        if (query_array.length > 0) {
          output_string = query_array.join(', ') + ', ';
        }
        let suggestions = [];
        for (let element of data.suggestions) {
          suggestions.push({'value': output_string + element})
        }
        console.log(suggestions);
        done({ suggestions: suggestions });
      }
    });
  }
});
