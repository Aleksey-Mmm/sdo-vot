function jq_ChainCombo(el) {
    var selected = $(el).find(':selected').data('id'); // get parent selected options' data-id attribute
    
    // get next combo (data-nextcombo attribute on parent select)
    var next_combo = $(el).data('nextcombo');
    
    // now if this 2nd combo doesn't have the old options list stored in it, make it happen
    if(!$(next_combo).data('store'))
        $(next_combo).data('store', $(next_combo).find('option')); // store data

    // now include data stored in attribute for use...
    var options2 = $(next_combo).data('store');

    // update combo box with filtered results
    $(next_combo).empty().append(
        options2.filter(function(){
            return $(this).data('option') === selected;
        })
    );
    
    // now enable in case disabled... 
    $(next_combo).prop('disabled', false);

    // now if this combo box has a child combo box, run this function again (recursive until an end is reached)
    if($(next_combo).data('nextcombo') !== undefined )
        jq_ChainCombo(next_combo); // now next_combo is the defining combo
}


// quick little jquery plugin to apply jq_ChainCombo to all selects with a data-nextcombo on them
jQuery.fn.chainCombo = function() {
// find all divs with a data-nextcombo attribute
$('[data-nextcombo]').each(function(i, obj) {
    $(this).change(function (){
        jq_ChainCombo(this);
    });
});
}();
