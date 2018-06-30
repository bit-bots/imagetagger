let annotation_filter = $('#annotation-filter-select');
let annotation_filter_input = $('#annotation-filter-input');
function setInput() {
  let selection = annotation_filter.val();
  switch (selection) {
    case 'older-than':
    case 'newer-than':
      annotation_filter_input.attr('type', 'date');
      break;
    case 'annotation-type':
    case 'latest-change-by':
      annotation_filter_input.attr('type', 'text');
      break;
    case 'verifications-min':
    case 'verifications-max':
      annotation_filter_input.attr('type', 'number');
      break;
    default:
      console.log(selection)
  }
}

annotation_filter.on('change', setInput);
setInput();