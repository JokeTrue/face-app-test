$(document).ready(function () {
    $('.hint .open').click(function () {
        var hint = $(this).parents().eq(2).find('input[name="hints"]');

        $(this).parent().next().find('.open').removeClass('blocked');
        $(this).remove();

        hint.val(parseInt(hint.val()) + 1);
    });
});