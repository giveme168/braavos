$(document).ready(function(){
  $("select").chosen({placeholder_text:"请选择...", disable_search_threshold: 10});
  $(".checkbox_all").click(function(){
    $(this).parents('table').find(".checkbox_one").prop('checked', $(this)[0].checked);
  });
  $(".checkbox_one").click(function(){
    if(!$(this)[0].checked){
      $(this).parents('table').find(".checkbox_all").prop('checked', false);
    }
  });
});
