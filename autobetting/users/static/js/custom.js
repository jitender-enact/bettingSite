$(document).on('click', ".clear", function () {
    $('input[type="text"]').each(function () {
        $(this).val("");
    })
});