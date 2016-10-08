$(document).ready(function(){
    $('.commit').click(function(){
        var status= $(this).val();
        ajaxGet(status);
    })


       function ajaxGet(status){

        var year=$('#year').find('span').html(),
            quarter=$('#quarter').find('span').html(),
            ret = {}, okrs, okrData, krData;

        ret['year'] = year;
        ret['quarter'] = quarter;
        ret['okrs'] = [];
        ret['status']=status;
        okrs = $(".OKR");

        if(okrs.length>0){
            for (var i = 0; i < okrs.length; i++){
                okr = okrs[i],
                okrData = {};
                okrData['objective']=$(okr).find('.edit_objective_area').html();
                okrData['priority'] = $(okr).find('.target').html();
                okrData['mid_eval_o'] = $(okr).find('#mid_eval').val();
                okrData['kr_items'] = [];
                var items=$(okr).find($('.okr_item')),
                    len = items.length;
                if(len>0){
                    for(var k=0; k<len; k++){
                        item = items[k],
                        krData = {};
                        krData['results'] = $(item).find('.edit_kr_area').html();
                        krData['results_PKR'] = $(item).find('.achievement_priority').html();
                        krData['mid_eval_kr'] = $(item).find('#mid_term_evaluation').val();
                        okrData['kr_items'] .push(krData);
                    }

                    ret['okrs'].push(okrData);

                }
            }

        }

        $('#okr_json').val($.toJSON(ret))
        $('#okr_form').submit();
    }

})
