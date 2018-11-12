function handleListElementClick(event) {
    $.each($('.list_element'), function (key, value) {
        $(value).removeClass('active');
    });
    $(event.target).parent().addClass('active');
}

let id = window.location.hash;

$(window).on('load', function () {
    $.each($('.list_element'), function (key, value) {
        let current_element = $(value);
        current_element.click(handleListElementClick);
        let current_a = $(current_element.find('a')[0]);
        if (current_a.attr('href') === id) {
            current_a.click();
        }
    });

    $('ul.nav-tabs.affix').css({
        width: $('#content-list').width()
    });
});