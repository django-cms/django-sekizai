# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import hashlib
import sass
from django.conf import settings
from django.contrib.staticfiles.finders import get_finders
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.template.base import Context
from django.template import Template
from django.utils.safestring import mark_safe
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.six.moves.urllib.request import url2pathname, pathname2url
from compressor.utils import get_class


class SassFileStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_ROOT  # could be replaced by SEKIZAI_ROOT
        if base_url is None:
            base_url = settings.STATIC_URL
        super(SassFileStorage, self).__init__(location, base_url, *args, **kwargs)


class SCSSProcessor(object):
    template = Template('<link href="{{ href }}"{% if type %} type="{{ type }}"{% endif %}{% if rel %} rel="{{ rel }}"{% endif %}{% if media %} media="{{ media }}"{% endif %} />')

    def __init__(self):
        self.Parser = get_class(settings.COMPRESS_PARSER)
        self.base_url = urlparse(settings.STATIC_URL)
        self.include_paths = []
        self.storage = SassFileStorage()
        self.md5 = hashlib.md5()
        self._hash_cache = {}
        for finder in get_finders():
            try:
                storages = finder.storages
            except AttributeError:
                continue
            for storage in storages.values():
                try:
                    self.include_paths.append(storage.path('.'))
                except NotImplementedError:
                    # storages that do not implement 'path' do not store files locally,
                    # and thus cannot provide an include path
                    pass

    def __call__(self, context, data, namespace):
        parser = self.Parser(data)
        attribs_list = []
        for elem in parser.css_elems():
            attribs = parser.elem_attribs(elem)
            attribs_list.append(attribs)
            href = attribs.get('href')
            if not (href and href.startswith(self.base_url[2])):
                attribs_list.append(attribs)
            sass_name = url2pathname(href[len(self.base_url[2]):])
            base_name, ext = os.path.splitext(sass_name)
            filename = self.find(sass_name)
            if not filename or ext != '.scss':
                continue
            # built the name of the compiled file and check if it already exists
            hashsum = self.file_hash(filename)
            css_name = '{0}.{1}.css'.format(base_name, hashsum)
            attribs['href'] = self.storage.url(css_name)
            if self.find(css_name):  # TODO: cache this information
                continue
            # otherwise compile the .scss file into .css and store it
            content = ContentFile(sass.compile(include_paths=self.include_paths, filename=filename))
            css_name = self.storage.save(css_name, content)
        return mark_safe(''.join(self.template.render(Context(ctx)) for ctx in attribs_list))

    def compile_offline(self, path):
            sass_name = url2pathname(path)
            base_name, ext = os.path.splitext(sass_name)
            sass_filename = self.find(sass_name)
            if not sass_filename or ext != '.scss':
                return
            hashsum = self.file_hash(sass_filename)
            css_name = '{0}.{1}.css'.format(base_name, hashsum)
            css_filename = os.path.join(sass_filename[:-len(sass_name)], css_name)
            content = sass.compile(include_paths=self.include_paths, filename=sass_filename)
            with open(css_filename, 'w') as fh:
                fh.write(content)

    def find(self, path):
        for finder in get_finders():
            result = finder.find(path)
            if result:
                return result

    def file_hash(self, filename):
        blocksize = 65536
        if filename in self._hash_cache:
            return self._hash_cache[filename]
        content = open(filename, 'rb')
        buf = content.read(blocksize)
        while len(buf) > 0:
            self.md5.update(buf)
            buf = content.read(blocksize)
        hashsum = self.md5.hexdigest()[:12]
        self._hash_cache[filename] = hashsum
        return hashsum

compilescss = SCSSProcessor()
