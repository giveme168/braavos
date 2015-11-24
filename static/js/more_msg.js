$(document).ready(function(){
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
//日历
    $('.wrap').rili({
        prevId:'prev',
        nextId:'next'
    });
})
//日历
;(function($){
$.fn.rili=function(options){
  options=$.extend({
    prevId:'prev',
    nextId:'next'
  },options)
  var nowDate=$(this).find('ul:first').addClass('nowDate');
  var otherDate=$(this).find('ul:last').addClass('otherDate');
  var $scrolling=$(this).find('#dates'),
      w=$(this).find('ul:first').outerWidth();
  var date=new Date(),
      year=date.getFullYear(),
      month=date.getMonth()+1,
      day=date.getDate();
    $('.curDate').text(year+'年'+month+'月');
    var days=getDays(year,month); 
    var weekStart=new Date(year,month-1,1).getDay(),
        str='';
    for(var i=0;i<weekStart;i++){
      str+='<li class="none"></li>'
    }
    for(var i=1; i<=days;i++){
      if(i==day){
        str+='<li class="on">'+i+'</li>'
      }else{
        str+='<li>'+i+'</li>';
      }
    }
    $('.nowDate').html(str);

$('#'+options.nextId).on('click',function(){
      month+=1;
      if(month>12){
        month=1;
        year+=1;
      }
    $('.curDate').html(year+'年'+month+'月');
    createRili(month);
    if(!$scrolling.is(':animated')){
      $scrolling.stop().animate({'marginLeft':-w},500,function(){
        $(this).find('ul:first').appendTo($scrolling).empty();
        $(this).css("marginLeft",0)
        $(this).find('ul:first').attr('class','nowDate');
        $(this).find('ul:last').attr('class','otherDate')
      });
    }

})
 $('#'+options.prevId).on('click',function(){
       month-=1;
       if(month<1){
         month=12;
         year-=1;
       }
       $('.curDate').text(year+'年'+month+'月');
       createRili(month);
       $scrolling.find('ul:last').prependTo($scrolling);
       $scrolling.css('marginLeft',-w);
       if(!$scrolling.is(':animated')){
         $scrolling.animate({'marginLeft':0},500,function(){
            $(this).find('ul:first').attr('class','nowDate');
            $(this).find('ul:last').attr('class','otherDate');
         });
       }
    })

function show(){
  $('#dates li').each(function(){
    if($(this).text()==day && $(this).text()==month){
             $(this).addClass('on');
          }
  })
  $('#dates li:not([class])').each(function(){
  $(this).on('click',function(){
    $(this).addClass('light').siblings().removeClass('light');
    alert($(this).html())
  })
})
}

show();
function createRili(mon){
  var date=new Date(year,mon-1,1),
      weekStart=date.getDay(),
      str='',i,
      countDays=getDays(year,mon);
      for(var i=0;i<weekStart;i++){
        str+='<li class="none"></li>'
      }
      for(var i=1;i<=countDays;i++){
        str+='<li>'+i+'</li>';
      }
    $('.otherDate').html(str);
    show();
}
function getDays(y,m){
  var countDay;
if(m==1 || m==3 || m==5 || m==8 || m==10 || m==12){
  countDay=31;
}else if(m==4 || m==6 || m==7 || m==9 || m==11){
  countDay=30;
}else{
  if(y%400==0 || (y%4==0 && y%100!=0)){
    countDay=29;
  }else{
    countDay=28;
  }
}
return countDay;
}
}
})(jQuery)