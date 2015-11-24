$(document).ready(function(){
	window.onload=function(){
		//var winWidth=$(window).width();
		//$('.menu').width(winWidth);
	$('.drop').click(function(){
		$('.menu').slideUp();
		$('.down').fadeIn();
	})
	$('.down').click(function(){
		$('.menu').slideDown();
		$(this).fadeOut();
	})
	$('.list li').click(function(){
		$(this).addClass('on').siblings().removeClass('on');
	})
	}
})