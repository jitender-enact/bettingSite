function hideShowQTRs(isShow) {
    // function display or hide QTRs tab from game intervals

    var game_interval = ["1", "2", "3"];  // display intervals
    if (isShow === true) {
        $("input[name=game_interval]").each(function () {
            $(this).parent("label").removeClass("hide");
        });
    } else {
        $("input[name=game_interval]").each(function () {
            if (game_interval.indexOf($(this).val()) < 0) {
                $(this).prop('checked', false);
                $(this).attr('checked', false);
                $(this).parent("label").removeClass("active").addClass("hide");
            }
        });
    }
}

function disableEnableQTRs(isEnable) {
    // function enable or disable QTRs tab from game intervals

    var game_interval = ["1", "2", "3"];  // display intervals
    if (isEnable === true) {
        $("input[name=game_interval]").each(function () {
            $(this).parent("label").removeClass("disabled");
            $(this).parent("label").attr('disabled', false);
            $(this).removeClass('disabled');
            $(this).prop('disabled', false);
            $(this).attr('disabled', false);
        });
    } else {
        $("input[name=game_interval]").each(function () {
            if (game_interval.indexOf($(this).val()) < 0) {
                $(this).prop('checked', false);
                $(this).attr('checked', false);
                $(this).prop('disabled', true);
                $(this).attr('disabled', true);
                $(this).addClass('disabled');
                $(this).parent("label").removeClass("active").addClass("disabled");
                $(this).parent("label").attr("disabled", true);
            }
        });
    }
}

$(document).on('click', ".game-type-label", function () {
    var sport_types = ["1", "2", "4"];
    var val = $(this).children('input').val();

    if (sport_types.indexOf(val) >= 0) {
        disableEnableQTRs(true);
    } else {
        disableEnableQTRs(false);
    }
});



$(document).on('click', "#clearbet", function () {
    $('input[type="text"]').each(function () {
        $(this).val("");
    })
});


$(document).on('click', "#showAll", function () {
    $("input[name=game_type]").each(function () {
        $(this).parent("label").removeClass("hide");
    });
    hideShowQTRs(true);
    $(this).addClass("hide");
    $("#showLess").removeClass("hide");
});


$(document).on('click', "#showLess", function () {
    var game_type = ["1", "2", "3", "4", "5", "6", "7"];
    var game_interval = ["1", "2", "3"];
    $("input[name=game_type]").each(function () {
        if (game_type.indexOf($(this).val()) < 0) {
            $(this).prop('checked', false);
            $(this).attr('checked', false);
            $(this).parent("label").removeClass("active").addClass("hide");
        }
    });
    hideShowQTRs(false);
    $(this).addClass("hide");
    $("#showAll").removeClass("hide");
});


$(document).on('click', ".selected-line-label", function () {
    var disable_incoming_line = ["3", "4"];
    var enable_incoming_line = ["1", "2"];
    var val = $(this).children('input').val();
    var ele = $("input[name=incoming_line]");
    if (disable_incoming_line.indexOf(val) >= 0 ) {
        // disable the incoming line
        ele.val("");
        ele.addClass("disabled");
        ele.attr({"disabled": true});
    }
    else if (enable_incoming_line.indexOf(val) >= 0) {
        // enable the incoming line
        ele.removeClass("disabled");
        ele.attr({"disabled": false});
    }
});


$(document).ready(function () {
    $('form[data-toggle="validator"]').validator({
        custom: {
            equalElem: function ($el) {
                var val = $.trim($el.val());
                var first_char = val[0];
                var ele = $("#betForm").find("input[name=selected_line]:checked");
                if ( ele.length > 0 ) {
                    //Spread
                    if ((ele.val() == "1") && (["-", "+"].indexOf(first_char) < 0 )) {
                        return "Must be start with -/+."
                    }
                    //total
                    else if((ele.val() == "2") && (["o", "u"].indexOf(first_char) < 0 )) {
                        return "Must be start with o/u."
                    }
                }
            }
        }
    });

});