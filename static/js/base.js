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

  $(".file-widget-button").change(function () {
    var data = new FormData();
    data.append('file', this.files[0]);
    var fileNameContainer = $(this).parents('.file-widget').find('.form-control');
    $.ajax({
            type:'POST',
            url: '/files/upload',
            data:data,
            cache:false,
            contentType: false,
            processData: false,
            success:function(data){
              if(data['status'] == '0'){
                fileNameContainer.val(data['filename']);
                fileNameContainer.trigger("change");
              }else{
                alert('上传失败啦!');
              }
            },
            error: function(data){
              alert('上传失败啦!');
            }
        });
  });
});
