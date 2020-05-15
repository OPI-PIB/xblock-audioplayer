"""TO-DO: Write a description of what this XBlock is."""
import json
import uuid

import pkg_resources
import requests
from django.core.files import File
from django.utils import translation
from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.settings import XBlockWithSettingsMixin

_ = lambda text: text
loader = ResourceLoader(__name__)


@XBlock.needs('settings')
@XBlock.needs('i18n')
class AudioPlayerXBlock(XBlockWithSettingsMixin, XBlock):
    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    display_name = String(display_name=_("Display Name"),
                          default=_("Audio Player"),
                          scope=Scope.settings,
                          help="")

    mp3_url = String(display_name=_("MP3 URL"),
                     default="https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/opiopc/b/opi_audio/o/mp3_file/059073bc-5624-4467-93e6-b59465d0b120",
                     scope=Scope.content,
                     help="")

    vtt_url = String(display_name=_("VVT Subtitles URL"),
                     default="https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/opiopc/b/opi_audio/o/vtt_file/0549e68f-e323-481b-b6e4-d0e3d9984d25",
                     scope=Scope.content,
                     help="")

    skip_flag = False
    block_settings_key = "AudioPlayerXBlock"

    def init_emulation(self):
        """
        Emulation of init function, for translation purpose.
        """
        if not self.skip_flag:
            i18n_ = self.runtime.service(self, "i18n").ugettext
            self.fields['display_name']._default = i18n_(
                self.fields['display_name']._default)
            self.skip_flag = True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_translation_content(self):
        try:
            return self.resource_string(
                '../public/js/translations/{lang}/text.js'.format(
                    lang=translation.get_language(),
                ))
        except IOError:
            return self.resource_string('../public/js/translations/en/text.js')

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the AudioPlayerXBlock, shown to students
        when viewing courses.
        """
        self.init_emulation()
        frag = Fragment()

        context = {
            'display_name': self.display_name,
            'mp3_url': self.mp3_url,
            'vtt_url': self.vtt_url,
        }

        frag.add_content(loader.render_django_template(
            "static/html/audioplayer.html",
            context=context,
            i18n_service=self.runtime.service(self, "i18n"),
        ))

        frag.add_css(loader.load_unicode("static/css/audioplayer.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url))

        frag.add_javascript(
            loader.load_unicode("static/js/src/vtt.js"))
        frag.add_javascript(
            loader.load_unicode("static/js/src/audiosync.js"))
        frag.add_javascript(
            loader.load_unicode("static/js/src/audioplayer.js"))
        frag.add_javascript(self.get_translation_content())
        frag.initialize_js('AudioPlayerXBlock')
        return frag

    def studio_view(self, context=None):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        self.init_emulation()
        frag = Fragment()

        context = {
            'display_name': self.display_name,
            'mp3_url': self.mp3_url,
            'vtt_url': self.vtt_url,
        }

        frag.add_content(loader.render_django_template(
            'static/html/audioplayer_edit.html',
            context=context,
            i18n_service=self.runtime.service(self, "i18n"),
        ))

        frag.add_javascript(
            loader.load_unicode("static/js/src/audioplayer_edit.js"))
        frag.initialize_js('AudioPlayerXBlockStudio')
        return frag

    @XBlock.json_handler
    def save_audioplayer(self, data, suffix=''):
        """
        The saving handler.
        """
        self.display_name = data['display_name']
        self.mp3_url = data['mp3_url']
        self.vtt_url = data['vtt_url']

        return {
            'result': 'success',
        }

    @XBlock.handler
    def save_file(self, request, suffix=''):
        """
        The saving handler.
        """
        upload = request.params['file']

        # upload.file.name
        print(request.params['key'])

        new_filename = request.params['key'] + "/" + str(uuid.uuid4())

        AUDIO_UPLOAD_URL = self.get_xblock_settings()['AUDIO_UPLOAD_URL']
        AUDIO_URL = self.get_xblock_settings()['AUDIO_URL']

        url = AUDIO_UPLOAD_URL + new_filename

        resp = requests.put(url, data=File(upload.file))

        response_data = ''
        if resp.status_code == 200:
            response_data = {
                'result': 'success',
                'url': AUDIO_URL + new_filename
            }

        return Response(json.dumps(response_data),
                        content_type='application/json',
                        charset='UTF-8')

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("AudioPlayerXBlock",
             """<audioplayer/>
             """),
            ("Multiple AudioPlayerXBlock",
             """<vertical_demo>
                <audioplayer/>
                <audioplayer/>
                <audioplayer/>
                </vertical_demo>
             """),
        ]

    @staticmethod
    def _get_statici18n_js_url():
        """
        Returns the Javascript translation file for the currently selected language, if any.
        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = 'public/js/translations/{locale_code}/text.js'
        lang_code = locale_code.split('-')[0]
        for code in (locale_code, lang_code, 'en'):
            loader = ResourceLoader(__name__)
            if pkg_resources.resource_exists(
                    loader.module_name, text_js.format(locale_code=code)):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Dummy method to generate initial i18n
        """
        return translation.gettext_noop('Dummy')
