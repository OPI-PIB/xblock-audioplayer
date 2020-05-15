var audioSync = function (options) {

    var audioPlayer = options.audioPlayer;
    var subtitles = options.subtitlesContainer;
    var syncData = [];

    fetch(new Request(options.subtitlesFile))
        .then(response => response.text())
        .then(createSubtitle);

    function createSubtitle(text) {
        convertVttToJson(text)
            .then((result) => {
                var x = 0;
                for (var i = 0; i < result.length; i++) { //cover for bug in vtt to json here
                    if (result[i].part && result[i].part.trim() != '') {
                        syncData[x] = result[i];
                        x++;
                    }
                }
            });
    }

    audioPlayer.bind("timeupdate", function (e) {
        syncData.forEach(function (element, index, array) {
            if ((e.target.currentTime * 1000) >= element.start && (e.target.currentTime * 1000) <= element.end) {
                $(subtitles).text(syncData[index].part)
            }
        });
    });
}
