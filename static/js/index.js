$(document).ready(function(){
/**
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
		if(this.Onchange==0){
			list[i].onmouseover=function(){
				changeOption(this.value);
			}
		}else if(this.Onchange==1){
			list[i].onclick=function(){
			changeOption(this.value);	
			}
		}else{

		}	
	}
	function autoplay(){
		_this.index++;
		if(_this.index>=list.length){
			_this.index=0;
		}
	changeOption(_this.index);
	_this.timer=setTimeout(autoplay,_this.auto[1]);
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
window.onload=function(){
	var tab1=new Tab();
	tab1.blind=['nav-title','li','con1','ul'];
	tab1.styles=['on','select'];
	tab1.Onchange=1;
	tab1.auto[0]=true;
	tab1.cure();

}

**/
$('.drown-click').click(function(e){
	e.stopPropagation();
	var ms=$('.down-menu', $(this).parent()).is(":hidden");
	$('.down-menu').slideUp()
	if(ms){
		$(this).parent().find('.down-menu').slideDown();
		$(this).find('.icon>img').animate({ "-webkit-transform": "rotate(90deg)","-moz-transform": "rotate(90deg)" }, 300 );
	}else{
		$(this).parent().find('.down-menu').slideUp();
	}

})
$(window).click(function(){
	$('.down-menu').slideUp();
})

$('.manage').mouseover(function(){
	$(this).css({
		background: '#352d1c',
	})
	$(this).find('p').show();
	$(this).find('h2').hide();

})

$('.manage').mouseleave(function(){
	$(this).css({
		background: '#919191'
	})
	$(this).find('p').hide();
	$(this).find('h2').show();
})






})













