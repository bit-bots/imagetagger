function initcheckbox()
{
    $('#img_form-group').hide();
    $('#img_agg').change(function () {
        if (this.checked) {
            $('#img_form-group').show();
            $('#base_content_noimg').hide();
            $('#base_content_img').show();
        }
        else {
            $('#img_form-group').hide();
            $('#base_content_noimg').show();
            $('#base_content_img').hide();
            this.prop('checked', false);
        }
    });
}
$(window).on('load', initcheckbox());
