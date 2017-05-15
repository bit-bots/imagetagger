var image_scale = 0;
$(document).ready(function () {
    init_navigationbuttons();
    // init_image();
    draw_box();
    $('div.filelist').animate({
        scrollTop: $("#selected_annotation_row").offset().top - 200}, 1000);

    $(document).keyup(function(event){
        /*switch(event.keyCode){
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
          case 82: //r
            $('#reset_button').click();
            break;
          case 32: //' '
            $('#annotation_form').submit();
            break;
        }*/
    });
});


$(window).resize(function() {
    image_scale = $('img#picture').get(0).naturalWidth / $('img#picture').width();
    draw_box();
});

function draw_box() {
    image_scale = $('img#picture').get(0).naturalWidth / $('img#picture').width();
    $('#boundingBox').css({
        'top': $('img#picture').attr('data-y')/image_scale-5,
        'left': $('img#picture').attr('data-x')/image_scale-2,
        'width': $('img#picture').attr('data-width')/image_scale,
        'height': $('img#picture').attr('data-height')/image_scale}); //todo: calibration
}
