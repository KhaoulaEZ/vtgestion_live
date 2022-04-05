// FDSelect handler
const mobile = $(window).width() <= 992;
const pc = $(window).width() >= 1200;
const desktop = $(window).width() >= 1800;
const switchSelect = (event) => {
    let _this = $(event.target)
    let theCase = _this.closest('.fdSelect').attr('id');
    if (theCase === 'dossierSwitcher') {
        // changer le dossier sur select header, ça demo la requete
        if (_this.hasClass('fdSelect_Options_Option')) {
            $('#dossierSwitcher > span').html(_this.text())
            const data = {
                id_client: _this.attr('data-type'),
                module: "change_dosser"
            }
            $('#selectedDossier').val(_this.attr('data-type'))
            if (_this.attr('data-type') !== $('#dossierSwitcher').attr('data-activedossier')) {
                $('#dossierSwitcher').attr('data-activedossier', _this.attr('data-type'))
                apiRequestHandler("pages/ajax.php", data)
            }

            $('.wrapp').height($('#headerInfos').outerHeight())
        } else {
            _this = _this.hasClass('fdSelect') ? _this : _this.parent()
            console.log(_this)
            if (!_this.hasClass('active') && mobile) {
                setTimeout(() => {
                    let a = $('header').outerHeight()
                    let b = $('#dossierSwitcher #fdSelect_Options').position().top + $('#dossierSwitcher #fdSelect_Options').outerHeight()
                    let c = $('#dossierSwitcher #fdSelect_Options').height()
                    let x = a - b
                    let y = c - x
                    a = a + y
                    console.log(a)
                    console.log(b)
                    console.log(c)
                    console.log(x)
                    console.log(y)
                    $('.wrapp').height(a)
                }, 400);
            } else {
                $('.wrapp').height($('#headerInfos').outerHeight())
            }
        }
    } else if (theCase === 'avisSelect') {
        if (_this.hasClass('fdSelect_Options_Option')) {
            $(`#${theCase} > span`).html(_this.text().trim())
        }
    } else {
        if (_this.hasClass('fdSelect_Options_Option')) {
            let old = $(`#${theCase} > span`).html().split(' ')[0]
            let now = $(`#${theCase} > span`).html().replace(old, _this.text().trim())
            $(`#${theCase} > span`).html(now)
        }
    }
    if ($(_this).hasClass('fdSelect')) {
        $(_this).toggleClass('active')
    } else {
        _this.parent().toggleClass('active')
    }
}
$('.fdSelect').on('click', (e) => switchSelect(e))
// End
// Global request sending function
const apiRequestHandler = (route, data) => {
    let url = ""
    let baseUrl = "https://www.fdmanager.fr/"
    url = baseUrl + (route[0] === '/' ? route.slice(1) : route)
    console.log(`Test request sent to : ${url} \n data: ${JSON.stringify(data)}`)
}
// End
// Nav sous menu (Dropdown)
$('.dropitdown').on('click', function (e) {
    e.preventDefault()
    let li = $(this).parent()
    li.toggleClass('activeDropDown')
    let height = 0
    if (li.hasClass('activeDropDown')) {
        $('.menu-item-dropdown').each((_, e) => {
            if ($(e).innerHeight() > height) {
                height = $(e).innerHeight()
            }
        })
        $("#dropdownbg").css({ height })
        $('.dropitdown').parent().addClass('activeDropDown')
    } else {
        $("#dropdownbg").css({ height: 0 })
        $('.activeDropDown').removeClass('activeDropDown')
    }

})
// End 
// Fermer les selects
$(window).click(function (event) {
    if (!$(event.target).hasClass('fdSelect') && $(event.target).parents().index("div.fdSelect") === -1) {
        $(".fdSelect").removeClass('active')
        // if ($('#headerNavbar').hasClass('open')) {
        //     $('.wrapp').height(0)
        // }
    }
})
// End fermer les selects
// Positionnement label pour input
$('.labelgroup>input, .labelgroup>textarea').keyup(function () {
    if ($(this).val() !== '') {
        $(this).parent().addClass('notempty');
    } else {
        $(this).parent().removeClass('notempty');
    }
})
// End
// See password login page
$('#seePassword').change(function () {
    if ($(this)[0].checked) {
        console.log($(this).siblings('#password'));
        $(this).siblings('#password').attr('type', 'text')
    } else {
        $(this).siblings('#password').attr('type', 'password')
    }
})

// END 
$('#phoneContainer').on('click', function () {
    placeCaretAtEnd(this)
})
$('#phoneContainer').on('paste', function (e) {
    e.preventDefault()
    if (e.clipboardData) {
        var text = e.clipboardData.getData('text/plain')
        document.execCommand('insertText', false, text)
    }
})
// Numero de telephone text area
const addedNumbers = []
$('#phoneContainer').on('DOMSubtreeModified', function () {
    let el = $(this).clone()
    el.find('span').remove()
    let a = el.html().trim()
    let x = a.match(/^(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:(?:[\s.-]?\d{2}){4}|\d{2}(?:[\s.-]?\d{3}){2})$/g);
    let phone = ""
    if (x) {
        let bu = x[0]
        x = x[0].trim().replaceAll(' ', '')
        if (x.slice(0, 2) === '00' || x[0] === '+') {
            if (x[0] === "+") {
                phone = `(+${x.slice(1, 3)})${x.slice(3, 7)}-${x.slice(7, 12)}`
            } else {
                phone = `(+${x.slice(2, 4)})${x.slice(4, 8)}-${x.slice(8, 13)}`
            }
        } else {
            phone = `(+33)${x.slice(1, 5)}-${x.slice(5, 11)}`
        }
        $(this).html($(this).html().replace(bu, ""))
        if (phone && addedNumbers.indexOf(x) === -1) {
            addedNumbers.push(x)
            $(this).append(`<span class="phone" contenteditable="false"><i class="fas fa-times" onclick="removeNumber(event)"></i>${phone}</span>`)
        }
        $(this).blur()
        placeCaretAtEnd(this)
    }
})

function placeCaretAtEnd(el) {
    el.focus();
    if (typeof window.getSelection != "undefined"
        && typeof document.createRange != "undefined") {
        var range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    } else if (typeof document.body.createTextRange != "undefined") {
        var textRange = document.body.createTextRange();
        textRange.moveToElementText(el);
        textRange.collapse(false);
        textRange.select();
    }
}
const isInt = (n) => {
    return n % 1 === 0;
}
const removeNumber = (e) => {
    $(e.target).parent().remove()
}
// END
// Animation stats dashbord
$('.numbers').each(function () {
    $(this).prop('Counter', 0).animate({
        Counter: $(this).text()
    }, {
        duration: 1500,
        easing: 'swing',
        step: function (now) {
            $(this).text(now.toFixed(now % 1 === 0 ? 0 : 1))

        },

    });

});
// END
// Hide header onscroll
var prevScrollpos = window.pageYOffset;
window.onscroll = function () {
    var currentScrollPos = window.pageYOffset;
    if ($(window).width() > 992) {
        if (prevScrollpos > currentScrollPos) {
            document.getElementById("headerContainer").style.top = "0";
            document.getElementById("fdContainer").style.marginTop = "115px";
        } else {
            if ($('body').height() > $(window).height() + 135) {
                document.getElementById("headerContainer").style.top = "-60px";
                document.getElementById("fdContainer").style.marginTop = "55px";
            }
        }
        prevScrollpos = currentScrollPos;
    }
}
// END
// Calcule view port
function vh(v) {
    var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    return (v * h) / 100;
}

function vw(v) {
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    return (v * w) / 100;
}
// END
// Toggle menu header
$('#toggleNav').click(function () {
    // let _this = $('header#headerNavbar')
    // _this.toggleClass('open')
    // if (_this.hasClass('collapsed')) {
    //     $('.wrapp').height($('#headerInfos').outerHeight())
    //     _this.removeClass('collapsed')
    // } else {
    //     $('.wrapp').height(0)
    //     _this.addClass('collapsed')
    // }
    if ($(this).attr('data-opened') !== 'true') {
        $(this).attr('data-opened', 'true')
        $('#fdContainer').css({ marginLeft: -vw(80), marginTop: $('#headerContainer').height() })
        $('#headerContainer').css({ marginLeft: -vw(80), position: 'fixed' })
        $('#rightSideMenu').css({ right: 0 })
    } else {
        $(this).attr('data-opened', '')
        $('#headerContainer').css({ marginLeft: '', position: '' })
        $('#fdContainer').css({ marginLeft: '', marginTop: '' })
        $('#rightSideMenu').css({ right: -vw(80) })

    }
})
// End
// jQuery datapicker
$('.datePicker').keydown(function (e) {
    e.preventDefault()
})
$('.date-from').datepicker({
    dateFormat: "dd/mm/yy",
    maxDate: "-1"
}).datepicker("setDate", new Date('11/12/2020'))
$('.date-to').datepicker({
    dateFormat: "dd/mm/yy",
    maxDate: "0"
}).datepicker("setDate", new Date())
$('.datePickerPlaceHolder,.date-label').click(function () {
    $($(this).siblings('.datePicker')[0]).focus()
})
$('.datePicker').change(function () {
    let date = new Date()
    let today = `${date.getDate()}/${date.getMonth() + 1 < 9 ? "0" + (date.getMonth() + 1) : date.getMonth() + 1}/${date.getFullYear()}`
    let picked = $(this).val()
    if (today === picked) {
        $($(this).siblings('.datePickerPlaceHolder')[0]).text("Aujourd'hui")
        $($(this).siblings('.datePickerPlaceHolder')[0]).css({ color: '' })
        $(this).css({ color: 'transparent' })
    } else {
        if ((parseInt(today.split('/')[0]) === parseInt(picked.split('/')[0]) + 1) && (parseInt(today.split('/')[1]) === parseInt(picked.split('/')[1])) && parseInt(today.split('/')[2]) === parseInt(picked.split('/')[2])) {
            $($(this).siblings('.datePickerPlaceHolder')[0]).text("Hier")
            $($(this).siblings('.datePickerPlaceHolder')[0]).css({ color: '' })
            $(this).css({ color: 'transparent' })
        } else {
            $($(this).siblings('.datePickerPlaceHolder')[0]).css({ color: 'transparent' })
            $(this).css({ color: '' })
        }
    }
})
// END
// Sortable images
$(".fdImageCardSortable").sortable();
// END
// subNav dropdown (gris)
$('.fdSubnav_link>a, .fdSubnav_link_dropdown').mouseenter(function () {
    if ($(this).hasClass('fdSubnav_link_dropdown')) {
        let height = $(this).innerHeight() + 50
        $('.fdSubnav').css({ height })
        $(this).css({ opacity: 1, visibility: 'visible' })
    } else {
        let itsdropdown = $(this).siblings('.fdSubnav_link_dropdown')
        let height = itsdropdown.innerHeight() + 50
        $('.fdSubnav').css({ height })
        itsdropdown.css({ opacity: 1, visibility: 'visible' })
    }
})
$('.fdSubnav_link').mouseout(function () {
    if (!$(this).children('.fdSubnav_link_dropdown').is(':hover')) {
        $('.fdSubnav').css({ height: "48" })
        $('.fdSubnav_link_dropdown').css({ opacity: '', visibility: '' })
    }
})
// END
// RIGHT DIV FOR TESTING

$('#settings').click(function () {
    $(this).toggleClass('active')
})

// END

// Leads page buttons alert testing
// Generating Ids
const makeFdID = () => {
    let result = '';
    const digits = '0123456789'
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    const characters = alphabet + alphabet.toLowerCase() + digits;
    const chatlength = characters.length;
    for (var i = 0; i < 10; i++) {
        result += characters.charAt(Math.floor(Math.random() * chatlength));
    }
    return result;
}
$('#testButtonContainer button').click(function () {
    const alertType = $(this).attr('class').replace('-outline', '').split('-')[1];
    const id = makeFdID()
    const template = `<div class="fdAlert-${alertType}" id="${id}">
        <p>Message de succès FUTUR DIGITAL</p>
        <button onclick="removeAlert('${id}')"><i class="fas fa-times"></i></button>
    </div>`
    $(this).parent().after(template);
})
// Remove alert

const removeAlert = (id) => {
    $('#' + id).remove()
}
// END

// OPEN Popup
$('.OpenPopup').click(function () {
    let _this = $(this)
    let popupName = _this.attr('data-popupName')
    $('.fdPopupCardContainer').removeClass('hidden')
    $(`#${popupName}Popup`).addClass('show')
})
$(document).keyup(function (e) {
    if (e.key === "Escape") {
        if (!$('.fdPopupCardContainer').hasClass('hidden')) {
            $('.fdPopupCardContainer').addClass('hidden')
            $('.fdPopupCard.show').removeClass('show')
        }
    }
});
$('button.closePopup').click(function () {
    $('.fdPopupCardContainer').addClass('hidden')
    $('.fdPopupCard.show').removeClass('show')
})
// END

// textarea typing tracking
$('.limitedTextArea').on('change keyup paste', function () {
    const valLength = $(this).val().length
    $(this).parent().siblings('.typingState').children('em').html((160 - valLength) + ' caractères restants')
});
// END