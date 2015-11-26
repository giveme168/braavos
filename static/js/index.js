$(document).ready(function(){
/************************* register event *********************************/	
//销售模块特效
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
// 销售 业务 公司 管理  模块 特效
$('.manage').mouseover(function(){
	_this=$(this);
	over_specially();
})
$('.manage').mouseleave(function(){
	_this=$(this);
	leave_specially();
	
})
//点击头像
$('.head-icon>img').click(function(e){
	e.stopPropagation();
	 $(this).addClass('on');
		my_message();
})
//点击菜单列表
$('.bussess').find('.drown-click').click(function(e){
		e.stopPropagation()
	var ms=$('.menu-list', $(this).parent()).is(":hidden");
	$('.menu-list').slideUp()
	if(ms){
		$(this).parent().find('.menu-list').slideDown();
	}else{
		$(this).parent().find('.menu-list').slideUp();
	}

})

$('.own-name').click(function(e){
	e.stopPropagation();
		my_message();
})
$('body').click(function(){
	$('.menu-list').slideUp();
	var Left=$('.head-icon').find('img').offset().left;
	var ms = $(".message");
	if (ms.is(":visible")){
		ms.animate({left:-(Left+120)+'px'}).fadeOut();
	}
})
/***************************** function define ********************************/
leave_specially=function(){
	_this.css({
		background: '#919191'
	})
	_this.find('p').hide();
	_this.find('h5').show();
} 
 over_specially=function(){	
	_this.css({
		background: '#352d1c',
	})
	_this.find('p').show();
	_this.find('h5').hide();
 }
my_message=function(){
	 var ms = $(".message");
	 var Left=$('.head-icon').find('img').offset().left;
	 if (ms.is(":hidden")){
	 	ms.show().animate({left:Left+120+'px'});
	 }else{ms.animate({left:-(Left+120)+'px'},function(){
	 		ms.fadeOut();
	 		})
		}
	 	
	}

})














