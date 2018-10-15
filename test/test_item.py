import datetime
import os
import unittest
import shutil
import satsearch.config as config
from stac.item import Item


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.dirname(testpath, 'test-item')

    @classmethod
    def _tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = os.path.join(testpath, config.DATADIR)

    def get_test_scene(self):
        """ Get valid test scene """
        return Item(self.item)

    def test_init(self):
        """ Initialize an item """
        scene = self.get_test_scene()
        dt, tm = self.item['properties']['datetime'].split('T')
        self.assertEqual(str(scene.date), dt)
        self.assertEqual(scene.id, self.item['properties']['id'])
        self.assertEqual(scene.geometry, self.item['geometry'])
        self.assertEqual(str(scene), self.item['properties']['id'])
        assert(list(scene.keys()) == ['id', 'collection', 'datetime', 'eo:platform'])

    def test_class_properties(self):
        """ Test the property functions of the Scene class """
        scene = self.get_test_scene()
        assert(scene.links['self']['href'] == 'link/to/self')
        assert(scene.bbox == [-71.46676936182894, 42.338371079679106, -70.09532154452742, 43.347431265475954])

    def test_assets(self):
        """ Get assets for download """
        scene = self.get_test_scene()
        assert(scene.assets['B1']['href'] == self.item['assets']['B1']['href'])
        assert(scene.asset('coastal')['href'] == self.item['assets']['B1']['href'])

    def test_download_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.download(key='thumbnail')
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        #shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def test_download(self):
        """ Retrieve a data file """
        scene = self.get_test_scene()
        fname = scene.download(key='MTL')
        self.assertTrue(os.path.exists(fname))
        fname = scene.download(key='MTL')
        assert(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        #shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def test_download_paths(self):
        """ Testing of download paths and filenames """
        scene = self.get_test_scene()
        datadir = config.DATADIR
        filename = config.FILENAME
        config.DATADIR = os.path.join(testpath, '${date}')
        config.FILENAME = '${date}_${id}'
        fname = scene.download('MTL')
        _fname = os.path.join(testpath, '2017-01-01/2017-01-01_testscene_MTL.txt')
        assert(fname == _fname)
        assert(os.path.exists(fname))
        config.DATADIR = datadir
        config.FILENAME = filename
        shutil.rmtree(os.path.join(testpath, '2017-01-01'))
        assert(os.path.exists(fname) == False)

    def test_download_nonexist(self):
        """ Test downloading of non-existent file """
        scene = self.get_test_scene()
        fname = scene.download(key='fake_asset')
        assert(fname is None)

    def test_download_all(self):
        """ Retrieve all data files from a source """
        scene = self.get_test_scene()
        fnames = [scene.download(a) for a in scene.assets if a != 'fake_asset']
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))

    def test_create_derived(self):
        """ Create single derived scene """
        scenes = [self.get_test_scene(), self.get_test_scene()]
        scene = Item.create_derived(scenes)
        assert(scene.date == scenes[0].date)
        assert(scene['c:id'] == scenes[0]['c:id'])
