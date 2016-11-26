var selection;
var image_scale = 0;

$(document).ready(function () {
    var image = $('img#picture');
    image_scale =  image.get(0).naturalWidth / image.width();
    selection = image.imgAreaSelect({
        instance: true,
        handles: true,
        minHeight: 10,
        minWidth: 10,
        onSelectChange: function (img, selection) {
            $('#x1Field').val(Math.ceil(selection.x1 * image_scale));
            $('#y1Field').val(Math.ceil(selection.y1 * image_scale));
            $('#x2Field').val(Math.floor(selection.x2 * image_scale));
            $('#y2Field').val(Math.floor(selection.y2 * image_scale));
        }
    });
    $('#x1Field')[0].oninput = function () {
        reload_selection();
    };
    $('#y1Field')[0].oninput = function () {
        reload_selection();
    };
    $('#x2Field')[0].oninput = function () {
        reload_selection();
    };
    $('#y2Field')[0].oninput = function () {
        reload_selection();
    };

    //$('#reset_button').click(reset_selection());

    $(this).on('mousemove touchmove', function(e) {
        var cH = $('#crosshair-h'), cV = $('#crosshair-v');
        image = $('img#picture');
        var position = image.offset();
        if((e.pageX > position.left && e.pageX < (position.left + image.width())) && (e.pageY > position.top && e.pageY < (position.top + image.height()))){
            cH.show();
            cV.show();
            $('#mousepos').show();

            cH.css('top', e.pageY +1);
            cV.css('left', e.pageX +1);

            $('#mousepos').css({
                top: (e.pageY) + 'px',
                left: (e.pageX)  + 'px'
            }, 800);
            $('#mousepos').text( "(" + Math.round((e.pageX - position.left)*image_scale) + ", " + Math.round((e.pageY - position.top)*image_scale) + ")");
            e.stopPropagation();
        }
        else{
            cH.hide();
            cV.hide();
            $('#mousepos').hide();
        }
    });

    $('#mousepos').hide();

		if (typeof init_navigationbuttons === "function") {
    	init_navigationbuttons();
      console.log('huhu!');
		}

		if (typeof loadannotation === "function") {
    	loadannotation();
			reload_selection();
      console.log('hihi!');
		}

});

$(window).resize(function() {
    selection.cancelSelection();
    image_scale = $('img#picture').get(0).naturalWidth / $('img#picture').width();
    console.log(image_scale);
});

function reload_selection() {
		selection = $('img#picture').imgAreaSelect({ instance: true, show: true });
    selection.setSelection(Math.round($('#x1Field').val() / image_scale), Math.round($('#y1Field').val() / image_scale), Math.round($('#x2Field').val() / image_scale), Math.round($('#y2Field').val() / image_scale));
    selection.update();
}

function reset_selection() {
    console.log('haha');
    $('#x1Field').val(0);
    $('#y1Field').val(0);
    $('#x2Field').val(0);
    $('#y2Field').val(0);
    selection.cancelSelection();
}
