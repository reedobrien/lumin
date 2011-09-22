from lumin.tests.base import BaseFunctionalTestCase


class TestMongoUploadTmpStore(BaseFunctionalTestCase):
    def make_one(self,
                 request=None,
                 gridfs=None,
                 image_mimetypes=('image/jpeg', 'image/png', 'image/gif'),
                 max_age=3600):
        from lumin.db import MongoUploadTmpStore
        if not request:
            request = self.request
        return MongoUploadTmpStore(request,
                                   gridfs=gridfs,
                                   image_mimetypes=image_mimetypes,
                                   max_age=max_age)

    def _make_fs(self):
        from gridfs import GridFS
        fs = GridFS(self.request.db, collection='tempstore')
        return fs

    def _make_fp(self, data='fp'):
        from cStringIO import StringIO
        return StringIO(data)

    def test_get_miss_explicit_default(self):
        inst = self.make_one()
        default = object()
        result = inst.get('uid', default)
        self.assertEqual(result, default)

    def test_get_miss_implicit_default(self):
        inst = self.make_one()
        result = inst.get('uid')
        self.assertEqual(result, None)

    def test_get_no_image(self):
        default = object()
        inst = self.make_one()
        result = inst.get('uid', default)
        self.assertEqual(result, default)

    def test_get_with_image(self):
        fs = self._make_fs()
        fp = self._make_fp()
        fs.put(fp, filename='abc', uid='theuid')
        default = object()
        inst = self.make_one(gridfs=fs)
        result = inst.get('theuid', default)
        self.failUnless('abc' in inst.fs.list())
        self.assertEqual(result['fp'].read(), 'fp')

    def test___getitem__miss(self):
        inst = self.make_one()
        self.assertRaises(KeyError, inst.__getitem__, 'uid')

    def test___getitem__hit(self):
        fs = self._make_fs()
        fp = self._make_fp()
        fs.put(fp, filename='abc', uid='uid', mimetype='atype')
        inst = self.make_one(gridfs=fs)
        self.assertEqual(inst['uid']['filename'], 'abc')
        self.assertEqual(inst['uid']['mimetype'], 'atype')
        self.assertEqual(inst['uid']['fp'].read(), self._make_fp().read())

    def test___contains__hit(self):
        fs = self._make_fs()
        fp = self._make_fp()
        fs.put(fp, filename='abc', uid='anuid')
        inst = self.make_one(gridfs=fs)
        self.assertEqual(inst.__contains__('anuid'), True)

    def test___contains__miss(self):
        inst = self.make_one()
        self.assertEqual(inst.__contains__('uid'), False)

    def test___setitem__(self):
        fp = self._make_fp()
        cstruct = {'fp': fp,
                   'mimetype': 'mimetype',
                   'filename': 'filename',
                   'uid': 'uid'}
        inst = self.make_one()
        inst['uid'] = cstruct
        one = self.request.db.tempstore.files.find_one({'uid': 'uid'})
        self.assertEqual(one['mimetype'], 'mimetype')
        self.assertEqual(one['uid'], 'uid')
        self.assertEqual(one['filename'], 'filename')
        self.assertEqual(one['length'], 2)
        self.failUnless(one['uploadDate'])
        self.failUnless(cstruct['filename'] in inst.fs.list())

    def test_preview_url(self):
        self.config.begin(request=self.request)
        self.config.add_route('preview_image', '/preview_image/:uid')
        fp = self._make_fp()
        fs = self._make_fs()
        inst = self.make_one(gridfs=fs)
        cstruct = {'fp': fp,
                   'mimetype': 'image/png',
                   'filename': 'filename',
                   'uid': 'uid'}
        inst['uid'] = cstruct
        self.assertEqual(inst.preview_url('uid'),
                         'http://example.com/preview_image/uid')

    def test_preview_url_not_image(self):
        self.config.begin(request=self.request)
        self.config.add_route('preview_image', '/preview_image/:uid')
        fp = self._make_fp()
        fs = self._make_fs()
        inst = self.make_one(gridfs=fs)
        cstruct = {'fp': fp,
                   'mimetype': 'text/html',
                   'filename': 'filename',
                   'uid': 'uid'}
        inst['uid'] = cstruct
        self.assertEqual(inst.preview_url('uid'), None)
