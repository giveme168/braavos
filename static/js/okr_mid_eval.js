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

                okrData['objective']=$('.okr_item').find('.edit_objective_area').val();
                okrData['priority'] = $('.okr_item').find('.target').html();
                okrData['mid_eval_o'] = $('.okr_item').find('#mid_eval').val();
                okrData['kr_items'] = [];
                var items=$(okr).find($('.okr_item')),
                    len = items.length;
                console.log(okrData)
                if(len>0){
                    for(var k=0; k<len; k++){
                        item = items[k],
                        krData = {};
                        krData['results'] = $(item).find('.edit_kr_area').val();
                        krData['results_PKR'] = $(item).find('.achievement_priority').html();
                        krData['mid_eval_kr'] = $(item).find('#mid_term_evaluation').val();
                        okrData['kr_items'] .push(krData);
                    }

                    ret['okrs'].push(okrData);

                }
            }

        }

        console.log(ret);
        $('#okr_json').val($.toJSON(ret))
    }

})
