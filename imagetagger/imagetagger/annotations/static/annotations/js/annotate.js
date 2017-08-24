var selection;
var image_scale = 0;

$(document).ready(function() {
  var selection;
  var image_scale = 0;
  var image = $('img#picture');

    $(function () {

      /*Setzt den Status auf verifiziert wenn das Objekt als nicht im Bild getagt ist*/
      $("#not_in_image").each(function(){
          if ($(this).is(":checked"))
              ReturnVal = true;
      });


      /*wenn content geladen setze die variable neu und wenn image_scale nicht größer 0 ist setze die globale variable neu und aktualisiere image_scale*/
      $( function() {

          selection = image.imgAreaSelect({
              instance: true,
              handles: false,
              minHeight: 2,
              minWidth: 2,
              onSelectChange: function (img, selection) {
                  $('#x1Field').val(Math.ceil(selection.x1 * image_scale));
                  $('#y1Field').val(Math.ceil(selection.y1 * image_scale));
                  $('#x2Field').val(Math.floor(selection.x2 * image_scale));
                  $('#y2Field').val(Math.floor(selection.y2 * image_scale));
              }
          });

          /*läd annotations*/
          if (typeof loadannotation === "function") { //tageditview
            loadannotation();
            reload_selection();
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

      $('#reset_button').click(reset_selection);

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
              cV.css("height", image.height() -1);
              cV.css("margin-top", position.top);
              cH.css("width", image.width() -1);
              cH.css("margin-left", position.left);
              if(!image_scale > 0) {
                  var image = $('img#picture');
                  image_scale =  image.get(0).naturalWidth / image.width();
              }

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

      if (typeof init_navigationbuttons === "function") { //tagview
        init_navigationbuttons();

          $(document).keyup(function(event){
              switch(event.keyCode){
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
                  case 71: //g
                      var nii = $('#not_in_image');
                      if(nii.prop('checked')) {
                          nii.prop('checked', false)
                      }
                      else {
                          nii.prop('checked', true)
                      }
                      break;
                  case 82: //r
                      $('#reset_button').click();
                      break;
                  case 86: //'v'
                      $('#annotation_form').submit();
                      break;
              }
          });

      }
  });


  //Änderung der Fenstergröße hebt Selektion auf und berechnet scale neu
  $(window).resize(function() {
      selection.cancelSelection();
      image_scale = $('img#picture').get(0).naturalWidth / $('img#picture').width();
  });

  //Wiederherstellung der Selektion
  function reload_selection() {
      selection = $('img#picture').imgAreaSelect({ instance: true, show: true });
      selection.setSelection(Math.round($('#x1Field').val() / image_scale), Math.round($('#y1Field').val() / image_scale), Math.round($('#x2Field').val() / image_scale), Math.round($('#y2Field').val() / image_scale));
      selection.update();
  }

  //Löschen der Selektion
  function reset_selection() {
      $('#x1Field').val(0);
      $('#y1Field').val(0);
      $('#x2Field').val(0);
      $('#y2Field').val(0);
      selection.cancelSelection();
  }

});
