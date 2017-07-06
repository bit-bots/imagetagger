var image_scale = 0;
$(document).ready(function () {
    init_navigationbuttons();
    // init_image();
    $('img#picture').on('load', function () {
        draw_box();
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
});


$(window).resize(function() {
    draw_box();
});

function draw_box() {
    image_scale = $('img#picture').get(0).naturalWidth / $('img#picture').width();
    $('#boundingBox').css({
        'top': $('img#picture').attr('data-y')/image_scale,
        'left': $('img#picture').attr('data-x')/image_scale,
        'width': $('img#picture').attr('data-width')/image_scale,
        'height': $('img#picture').attr('data-height')/image_scale}); //todo: calibration
}
