$(document).ready(function(){
    //库存表格表头停留
    $('.reserve_mod a:eq(0)').addClass('side-item-on');
    var attached = false,
    top_table = $('.top-attached-table'),
    topThead = null,
    $tbl = $('#storage-table'),
    pos_top_scroll = $tbl.offset().top;
    $(window).scroll(function(e){
        var $thead = $tbl.find('thead.real'),
        $target = $(e.target),
        _width = $thead.width();
        scroll_top = $target.scrollTop();
        if (scroll_top > pos_top_scroll && attached == false) {
            attached = true;
            top_table.css({
             position:'fixed',
             top: '0px',
             width: _width
             }).show();
             $($(".chosen-container")[1]).hide();
         }
         if (scroll_top < pos_top_scroll && attached == true) {
             attached = false;
             top_table.hide();
             $($(".chosen-container")[1]).show();
         }
    });

    // 获得位置当天的详细信息
    var force_cell = false
    function storage_info_stat(storage_info){
        var header = "<li class='storage-stat'><h4>资源情况</h4>";
        header += "<ul>";
        header += "<li class='item'>资源总量:"+storage_info["estimate_num"]+"</li>";
        header += "<li class='item'>已下单总量:"+storage_info["ordered_num"]+"</li>";
        header += "<li class='item'>预下单总量:"+storage_info["per_ordered_num"]+"</li>";
        header += "<li class='item'>剩余总量:"+storage_info["remain_num"]+"</li>";
        header += "</ul>";
        header += "</li>";
        return header;
    }
    function storage_info_order(order_info){
        var order = "<li class='schedule-order'>";
        order += "<ul>";
        order += "<li class='item'><a href='"+order_info["URL"]+"'>"+order_info["name"]+"</a></li>";
        order += "<li class='item'>预订量:"+order_info["occupy_num"]+"</li>";
        order += "<li class='item'>状态:"+order_info["state_cn"]+"</li>";
        order += "<li class='item'>时间:"+order_info["date_cn"]+"</li>";
        order += "<li class='item'>定向/定投:"+order_info["special_sale"]+"</li>";
        order += "<li class='item'>创建者:"+order_info["creator"]+"</li>";
        order += "</ul>";
        order += "</li>";
        return order;
    }
    $('.cell').click(function(){
        force_cell = true
        date = $(this).attr('date');
        position_id = $(this).attr('position')
        var e = window.event;
        var x=(e.clientX+document.body.scrollLeft-285);
        var y=e.clientY+document.body.scrollTop-21;
        $("#storage_info").css({
            position:'absolute',
            top:y,
            left:x
        }).show("slow")
        $.getJSON('/storage/storage_info?date='+date+'&position_id='+position_id,
            function(result){
                var storage_info_content = storage_info_stat(result);
                if (result["orders"].length) storage_info_content += "<h4>订单信息</h4>"
                for (var o in result["orders"]){
                    storage_info_content += storage_info_order(result["orders"][o])
                }                
                $("#storage_info").find(".storage").html(storage_info_content);
            });
        $("#storage_info").find(".loading").hide();
    });
    $("body").click(function(){
        if(!force_cell){
            $("#storage_info").hide("slow");
        }
        else force_cell = false       
    });
});
