/* Javascript for AudioPlayerXBlock. */
function AudioPlayerXBlock(runtime, element) {


    $(document).ready(function () {
        var audioPlayer = $("#audiofile", element);
        var subtitles = $("#subtitles", element);

        var options = {
            audioPlayer: audioPlayer,
            subtitlesContainer: subtitles,
            subtitlesFile: $("#subtitles_url").val()
        };

        audioSync(
            options
        );
    });


    $(function ($) {
        /*
        Use `gettext` provided by django-statici18n for static translations

        var gettext = AudioPlayerXBlocki18n.gettext;
        */

        /* Here's where you'd do things on page load. */
    });
}
