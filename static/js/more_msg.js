$(document).ready(function(){
    on_show()
})
function on_show(){
  var btns = $('#button');
    var content = $("#content");
    $("li", btns).click(function(){
        $('p', this).addClass('select');
        $('span', this).addClass('select');
        var content = $(".content", this).html();
        $("#content").find(".con").html(content);
        $(this).siblings().find("p").removeClass("select");
        $(this).siblings().find("span").removeClass("select")
    })
}