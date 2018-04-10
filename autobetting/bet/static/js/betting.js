$(document).on('click', "#clearbet", function () {
    $('input[type="text"]').each(function () {
        $(this).val("");
    })
});


$(document).on('click', "#showAll", function () {
    $("input[name=game_type]").each(function () {
        $(this).parent("label").removeClass("hide");
    });
    $("input[name=game_interval]").each(function () {
        $(this).parent("label").removeClass("hide");
    });
    $(this).addClass("hide");
    $("#showLess").removeClass("hide");
});


$(document).on('click', "#showLess", function () {
    var game_type = ["1", "2", "3", "4", "5", "6", "7"];
    var game_interval = ["1", "2", "3"];
    $("input[name=game_type]").each(function () {
        if (game_type.indexOf($(this).val()) < 0){
            $(this).prop('checked', false);
            $(this).attr('checked', false);
            $(this).parent("label").removeClass("active").addClass("hide");
        }
    });
    $("input[name=game_interval]").each(function () {
        if (game_interval.indexOf($(this).val()) < 0){
            $(this).prop('checked', false);
            $(this).attr('checked', false);
            $(this).parent("label").removeClass("active").addClass("hide");
        }
    });
    $(this).addClass("hide");
    $("#showAll").removeClass("hide");
});