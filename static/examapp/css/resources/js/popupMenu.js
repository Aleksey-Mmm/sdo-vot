function popupMenu(ctlClass, popupElementId) {
    $(document).click(function() {
        $("#" + popupElementId).hide();
    });
    $("."+ctlClass).click(function (event) {
        var ctl = $(event.currentTarget).prev();
        var popup = $("#" + popupElementId);
        popup.show();
        popup.css("left", ctl.offset().left + 20);
        popup.css("top", ctl.offset().top + ctl.height()+5);
        popup.css("min-width", ctl.width());
        event.stopPropagation();
    });
}