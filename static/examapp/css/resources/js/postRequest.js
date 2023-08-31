function sendPostRequest(url, cb, refreshPage) {
  $.ajax({
    url: url,
    type: 'POST',
    success: cb
  }).done(function () {
    if(refreshPage){
      window.location.reload();
    }
  });
}

function sendPostRequestWithConfirm(confirmText, url, refreshPage) {
  if(confirm(confirmText)) {
    sendPostRequest(url, null, refreshPage);
  }
}

function deleteFile(fileName, fileId, redirect) {
  sendPostRequest('/' + fileName + '/' + fileId + '/deleteFile' + (redirect !== null ? '?redirect=' + redirect : ''));
}

function url_redirect(options){
     var $form = $("<form />");

     $form.attr("action",options.url);
     $form.attr("method",options.method);

     for (var data in options.data)
     $form.append('<input type="hidden" name="'+data+'" value="'+options.data[data]+'" />');

     $("body").append($form);
     $form.submit();
}
