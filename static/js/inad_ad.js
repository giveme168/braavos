function test(data){
    if (data.msg) {
        return '';
    } else {
        var html = data.html || '',
            width = data.width || 0,
            height = data.height || 0,
            divEl = window.document.getElementById('inad_' + ADSCODE);
    
        //create iframe
        var ifrm = window.document.createElement('iframe');
        ifrm.width = width;
        ifrm.height = height;
        ifrm.frameBorder = 0;
        ifrm.scrolling = 'no';
        ifrm.id='inad_'+ADSCODE+'_show';
        divEl.appendChild(ifrm);
        
        var doc = document.getElementById('inad_'+ADSCODE+'_show').contentDocument || document.frames('inad_' + ADSCODE + '_show').document;
        doc.write(html);
        doc.close();
    }
}

var url = 'http://r.inad.com/req/?unit=' + ADSCODE+'&callback=test',
    newScript=window.document.createElement('script'),
    firstScript=window.document.getElementsByTagName('script')[0];
    newScript.setAttribute('type', 'text/javascript');
    newScript.setAttribute('src', url);
    firstScript.parentNode.insertBefore(newScript, firstScript);