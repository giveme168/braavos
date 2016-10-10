$(document).ready(function () {

    $('.add').click(function () {

        var str = '';
        str += '<tbody class="OKR"><tr class="okr_item">' +
            '<td rowspan="" class="merge_row"><textarea class="form-control objective" rows="8" name="comment"></textarea></td>' +
            '<td rowspan="" class="merge_row">' +
            '<select name="" form-control class="form-control input-sm obj_weight">' +
            '<option value="P0">P0</option>' +
            '<option value="P1">P1</option>' +
            '<option value="P2">P2</option>' +
            '<option value="P3">P3</option>' +
            '</select>' +
            '</td>' +
            '<td>' +
            '<button type="button" class="btn add_kr" style="float:right">添加KR</button>' +
            '<textarea class="form-control key_result" rows="2"></textarea></td>' +
            '<td class="">' +
            '<select name="" id="" form-control class="form-control input-sm weighted">' +
            '<option value="P0">P0</option>' +
            '<option value="P1">P1</option>' +
            '<option value="P2">P2</option>' +
            '<option value="P3">P3</option>' +
            '</select>' +
            '</td>' +
            '<td rowspan="" class="merge_row"><button type="button" class="btn delete">删除</button></td>' +
            '</tr>' +
            '</tbody>';

        $('.wrapper table').append($(str));
        $('select').chosen({disable_search: true});
    })

    $('.wrapper').delegate('.delete', 'click', function () {
        $(this).parents('tbody').remove();
    })

    $('.commit').click(function () {
        var status = $(this).val();
        ajaxGet(status);
    })

    $('.wrapper').delegate('.add_kr', 'click', function () {
        var data = '';
        data += '<tr class="okr_item">' +
            '<td class="Key_results">' +
            '<textarea class="form-control key_result" rows="2"></textarea>' +
            '</td>' +
            '<td class="">' +
            '<select name="" id="" form-control class="form-control input-sm weighted">' +
            '<option value="P0">P0</option>' +
            '<option value="P1">P1</option>' +
            '<option value="P2">P2</option>' +
            '<option value="P3">P3</option>' +
            '</select>' +
            '<button type="button" class="btn delete_okr">删除KR</button>' +
            '</td>' +
            '</tr>';

        $(this).parents('.OKR').append($(data));

        var okrLen = $(this).parents('.OKR').find('.okr_item').size();
        $(this).parents('.OKR').find('.merge_row').attr('rowspan', okrLen);
        $('select').chosen({disable_search: true});

    })


    $('.wrapper').delegate('.delete_okr', 'click', function () {
        var okrLen = $(this).parents('.OKR').find('.okr_item').size() - 1;
        $(this).parents('.OKR').find('.merge_row').attr('rowspan', okrLen);
        $(this).parents('.okr_item').remove();
    })

    function ajaxGet(status) {

        var year = $('#year').find('select').val(),
            quarter = $('#quarter').find('select').val(),
            ret = {}, okrs, okrData, krData;
        ret['year'] = year;
        ret['quarter'] = quarter;
        ret['okrs'] = [];
        ret['status'] = status;
        okrs = $(".OKR");

        if (okrs.length > 0) {
            for (var i = 0; i < okrs.length; i++) {
                okr = okrs[i],
                    okrData = {};

                okrData['objective'] = $(okr).find('.objective').val();
                okrData['priority'] = $(okr).find('.obj_weight').val();
                okrData['kr_items'] = [];

                var items = $(okr).find($('.okr_item')),
                    len = items.length;

                if (len > 0) {
                    for (var k = 0; k < len; k++) {
                        item = items[k],
                            krData = {};
                        krData['results'] = $(item).find('.key_result').val();
                        krData['results_PKR'] = $(item).find('.weighted').val();

                        okrData['kr_items'].push(krData);
                    }
                    ret['okrs'].push(okrData);

                }
            }

        }

        console.log(ret);
        $('#okr_json').val($.toJSON(ret))
        /**
         $.ajax({
            url: "/account/okr/create_json",
            type:'POST',
            data:{'okr':},
            success:function(data){

            }

        })*/
    }

    $('.wrapper select').chosen({disable_search: true});
})


