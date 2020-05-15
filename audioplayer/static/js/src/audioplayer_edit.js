function AudioPlayerXBlockStudio(runtime, element) {

    $(element).find('.action-cancel').bind('click', function () {
        runtime.notify('cancel', {});
    });


    $(".upload_file").change(function () {
        var fd = new FormData();
        var files = $(this)[0].files[0];
        fd.append("file", files);

        var key = $(this).attr("name");
        fd.append("key", key);

        $.ajax({
            url: runtime.handlerUrl(element, 'save_file'),
            type: 'post',
            data: fd,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response != 0) {
                    alert(response['result']);
                    $("#" + key.replace("_file", "_url")).val(response['url'])
                } else {
                    alert('file not uploaded');
                }
            },
        });
    });

    $(element).find('.action-save').bind('click', function () {
        var data = {
            'display_name': $('#display_name').val(),
            'mp3_url': $('#mp3_url').val(),
            'vtt_url': $('#vtt_url').val(),
        };

        runtime.notify('save', {state: 'start'});

        var handlerUrl = runtime.handlerUrl(element, 'save_audioplayer');
        $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
            if (response.result === 'success') {
                runtime.notify('save', {state: 'end'});
                // Reload the whole page :
                // window.location.reload(false);
            } else {
                runtime.notify('error', {msg: response.message})
            }
        });
    });

}