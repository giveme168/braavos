$(document).ready(function(){
    $('.datetimepicker').datetimepicker({
        autoclose: true,
        todayHighlight: true,
        language: 'zh-CN',
        minView: 2
      });
    // 新建一个展示位置的排期
    $(".schedule-add").click(function(){
      var schedule_tpl = $("#schedule-tpl").html(); 
      $(this).parents(".schedule-saletype").find("#schedule-content").append(schedule_tpl);

      load_schedule($(this).parents(".schedule-saletype").find(".schedule-form").last().find(".position"));
      $(this).parents(".schedule-saletype").find(".schedule-form").last().find(".form-description").hide();
    });
    // 删除排期
    $("body").on('click', ".schedule-delete", function(){
        $(this).parents(".schedule-form").remove(); 
    });
 
    // 排期表单 单元
    function schedule_td(schedule){
        var weekday = schedule[2],
            workday_or_weekend = 'workday';
        if(weekday == 6){ workday_or_weekend = 'weekend'; }
        if(weekday == 7){ workday_or_weekend = 'weekend'; }
        if((schedule[1])>0){
          var td = '<td class="weekday-'+weekday+
            ' ' + workday_or_weekend + 
            '"><div class="sch-date">' + 
            schedule[0] + 
            '</div><div class="sch-num">' +
            '<input type="text" class="order-num" name="' + schedule[0] +
            '" value="0" data-max="'+schedule[1]+'"/>' + ' / '+ schedule[1] +'</div></td>';
        }
        else{
          var td = '<td><div class="sch-date">' + schedule[0] + '</div><div class="sch-num">无资源</div></td>';
        }
        if(weekday == 1){ td = '<tr>' + td; }
        if(weekday == 7){ td = td + '</tr>';}
        return td;
    }
    // 排期表单 单元
    function schedule_header(schedule){
        var _content = '<tr> <th class="info">周一</th> <th class="info">周二</th> <th class="info">周三</th> <th class="info">周四</th> <th class="info">周五</th> <th class="success">周六</th> <th class="success">周日</th></tr>',
        weekday = schedule[2];
        if(weekday > 1){
          _content = _content + '<tr>';
          for(var i=1; i < weekday; i++ )
          {
              _content = _content + '<td></td>';
          }
        }
        return _content;
    }
    // 从服务器load该展示位置的排期数据
    function load_schedule(position){
      var start = $("#start_date").val(),
      end = $("#end_date").val();
      $.getJSON('/schedule/schedule_info/?start='+start+'&end='+end+'&position='+position.val(),
          function(result){
            table_content = schedule_header(result['schedules'][0]);
            for(var x in result['schedules']){
                table_content = table_content + schedule_td(result['schedules'][x]);
            }
            position.parents(".schedule-form").find("#schedule-table").html(table_content);
          });
    }
    set_readonly_by_date = function(){
        schedules = $('.schedule-form').find(".order-num")
        for(var x=0; x<schedules.length; x++){
            var schedule = schedules[x];
            if(!check_date($(schedule).attr("name"))){
                $(schedule).attr("readonly",true);
            }
        }
    }
    check_date = function(date_str){
        var date_arr = date_str.split("-");   
        var date = new Date(date_arr[0],parseInt(date_arr[1])-1,parseInt(date_arr[2])+1); 
        var today = new Date();
        return date>=today;
    }
    set_readonly_by_date();
    // 展示位置改变, 重新加载数据
    $("body").on('change', ".position-select", function(){
      load_schedule($(this));
    });
    // 展示位置特殊投放
    $("body").on('change', ".special_sale", function(){
        if($(this).val() == '0'){
            $(this).parents('.schedule-form').find('.form-description').hide();
        }else{
            $(this).parents('.schedule-form').find('.form-description').show();
        }
    });
    // 预订数量改变
    $("body").on('keyup', ".order-num", function(){
        check_all_order_num();
    });
    check_all_order_num = function(){
        var forms = $('.schedule-form');
        for(var x=0; x<forms.length; x++){
          var form = forms[x],
              sum = get_sum_and_check_order_num($(form).find(".order-num"));
          $(form).find(".schedule-sum").html(sum);
        }
    }
    function get_sum_and_check_order_num(schedules){
      var sum = 0;
      if(schedules.length > 0){
        for(var x=0; x<schedules.length; x++){
          var schedule = schedules[x];
          if($(schedule).val() > 0){
            var max = parseInt($(schedule).data('max')),
                val = parseInt($(schedule).val());
            sum = sum + val;
            if(val > max){
                $(schedule).parent().parent().addClass('danger');
            }else{
                $(schedule).parent().parent().removeClass('danger');
            }
          }
        }
      }
      return sum;
    }
    // 快速预订
    $("body").on('click', ".speed-workday", function(){
        var speed_val = $(this).parent().parent().find('.speed-value').val();
        $(this).parents('.schedule-form').find('.workday').find('.order-num').val(speed_val);
        check_all_order_num();
    });
    $("body").on('click', ".speed-weekend", function(){
        var speed_val = $(this).parent().parent().find('.speed-value').val();
        $(this).parents('.schedule-form').find('.weekend').find('.order-num').val(speed_val);
        check_all_order_num();
    });
    $("body").on('click', ".speed-all", function(){
        var speed_val = $(this).parent().parent().find('.speed-value').val();
        $(this).parents('.schedule-form').find('.order-num').val(speed_val);
        check_all_order_num();
    });
    // 整理要提交的排期数据
    get_form_schedule_data = function(schedules){
      var ret = {};
      if(schedules.length > 0){
        for(var x=0; x<schedules.length; x++){
          var schedule = schedules[x];
          if($(schedule).val() > 0){
            ret[schedule.name] = $(schedule).val();
          }
        }
      }
      return ret;
    }
    get_form_all_data = function(){
        var ret = [];
        if($(".schedule-form").length > 0){
          for(var x=0; x<$(".schedule-form").length; x++){
              var form = $(".schedule-form")[x],
              form_data = {};
              form_data['sale_type'] = $(form).parent().data('saletype');
              form_data['special_sale'] = $(form).find(".special_sale").val();
              if(form_data['special_sale'] == '0'){
                form_data['description'] = "";
              }else{
                form_data['description'] = $(form).find(".description").val(); 
              }
              form_data['position'] = $(form).find(".position").val();
              form_data['schedule'] = get_form_schedule_data($(form).find(".order-num"));
              if(!$.isEmptyObject(form_data['schedule'])){ ret.push(form_data);}
          }
        }
        return ret;
    }
    function check_sent_data(sent_data){
      if(sent_data.length==0){
        alert("所有排期项都为空!");
        return false;
      }
      // 检查是否有相同售卖类型+展示位置   同一个售卖类型下, 相同展示位置只能有一个排期
      var unique_schedule = [];
      for(var x in sent_data){
        schedule = sent_data[x];
        var schedule_str = "type:"+schedule['sale_type']+"position:"+schedule['position'];
        if($.inArray(schedule_str, unique_schedule) > -1){
            alert("每种售卖类型下(购买, 配送, 补量), 相同的展示位置只能预订一次, 如有重复, 请合并成一个排期项!");
            return false;
        }else{
            unique_schedule.push(schedule_str);
        }
      }
      return true;
    }
    function post_schedules(sent_data){
      if(check_sent_data(sent_data)){
        $.post('/schedule/order/'+order_id+'/schedules_post/',
          {data: $.toJSON(sent_data)},
          function(data) {
            if(data['status'] == '0'){
            window.location.href = "/schedule/order/"+order_id+"/0";
            }
            else{
              alert(data['msg']);
            }
          },
          'json'); 
      }
    }
    $("#form-submit").click(function(){
        if($(".schedule-form").length==0){alert("请先新建排期项!");}
        else{ post_schedules(get_form_all_data());}
    });
});
