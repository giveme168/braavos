$(document).ready(function(){
/************************* register event *********************************/    
    window.onload=function(){
        var tab1=new Tab();
        tab1.blind=['nav-title','li','con1','ul'];
        tab1.styles=['on','select'];
        tab1.Onchange=1;
        tab1.auto[0]=true;
        tab1.cure();
    }
    function Tab(){
        this.blind=[];
        this.styles=[];
        this.Onchange=0;
        this.auto=[false,1000];
        this.timer=null;
        this.index=0;
    }
    Tab.prototype.$=function(id){
        return typeof id==='string'?document.getElementById(id):id;
    }
    Tab.prototype.cure=function(){
        var list=this.$(this.blind[0]).getElementsByTagName(this.blind[1]),
            uls=this.$(this.blind[2]).getElementsByTagName(this.blind[3]);
            if(list.length!=uls.length) return;
                var _this=this;
        for(var i=0;i<list.length;i++){
            list[i].value=i;
            if(this.Onchange==1){
                list[i].onclick=function(){
                changeOption(this.value);   
                }
            }
        }
    //鼠标划过
    changeOption=function(curIndex){
    for(var a=0;a<list.length;a++){
        list[a].className="";
        uls[a].className="";
    }
    list[curIndex].className=_this.styles[0];
    uls[curIndex].className=_this.styles[1];
    _this.index=curIndex;
    }
}
//点击头像
$('.head-icon>img').click(function(e){
    e.stopPropagation();
     $(this).addClass('on');
        my_message();
})

$('.own-name').click(function(e){
    e.stopPropagation();
        my_message();
})


$('body').click(function(){
    var Left=$('.head-icon').find('img').offset().left;
    var ms = $(".message");
    if (ms.is(":visible")){
        ms.animate({left:-(135)+'px'}).fadeOut();
    }
})

$('.bussess').find('img').mouseover(function(){
    var list=$(this).attr('src');
        array = list.split('.')
        str=array[0]+"_selected";
        $(this).attr("src",str+'.png')
})

$('.bussess').find('img').mouseout(function(){
    var list=$(this).attr('src');
        array = list.split('_selected')
        str=array[0]
        $(this).attr("src", str+'.png')
})

my_message=function(){
     var ms = $(".message");
     if (ms.is(":hidden")){
        ms.show().animate({left:135+'px'});
     }else{ms.animate({left:-(135)+'px'},function(){
            ms.fadeOut();
            })
        }
        
    }

})



