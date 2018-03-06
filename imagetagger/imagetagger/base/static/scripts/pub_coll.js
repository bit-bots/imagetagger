$(document).ready(function () {
    var pub_coll_check = $('#id_public_collaboration');
    var pub_check = $('#id_public');
    if (pub_check.prop('checked')){
        pub_coll_check.prop('disabled', false);
    }
    else {
        pub_coll_check.prop('disabled', true);
    }
    pub_check.click(function(){
        pub_coll_check.prop('checked', false).change();
        if ($('#id_public').prop('checked')){
            pub_coll_check.prop('disabled', false);
        }
        else {
            pub_coll_check.prop('disabled', true);
        }
    });
});


