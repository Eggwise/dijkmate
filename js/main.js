/**
 * Created by jonathan on 10/10/16.
 */



var id_button_menu = 'button_menu';
var class_button_menu = 'ui button';


window.onload = (function () {


    // overview()
    console.log('window palla')

    $('#'+id_button_menu).click(on_button_menu_click)
})

function on_button_menu_click(event) {

    var button = $(event.target)
    // button.addClass('active')
    // console.log(event.target.className(class_button_menu))
    console.log('buttn palla')
    overview()
}

function overview() {
    Reveal.toggleOverview();
}
