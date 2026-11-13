import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image

SPEC = importlib.util.spec_from_file_location('contract', Path(__file__).parents[1]/'scripts/cover_contract.py')
c = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(c)


class ContractTests(unittest.TestCase):
    def test_selected_profiles_and_dedup(self):
        p = c.plan(['douyin','bilibili','x-article','wechat-article','douyin'])
        self.assertEqual(len(p['placements']), 7)
        self.assertEqual(len(p['assets']), 6)
        self.assertEqual({(x['width'],x['height']) for x in p['assets']},
                         {(1080,1440),(1440,1080),(1920,1080),(2000,800),(1880,800),(800,800)})
        self.assertFalse(any(x['height']==1920 for x in p['assets']))

    def test_square_crop_not_reused_as_generated_square(self):
        p=c.plan(['wechat-article','wechat-square'])
        self.assertEqual(len(p['assets']),3)
        self.assertNotEqual(p['placements'][1]['assetId'],p['placements'][2]['assetId'])

    def test_missing_and_wrong_size_fail(self):
        p=c.plan(['x-article'])
        with tempfile.TemporaryDirectory(prefix='cover test ') as d:
            root=Path(d)
            self.assertFalse(c.verify(p,root)['fileChecksPassed'])
            Image.new('RGB',(1024,768)).save(root/p['assets'][0]['path'])
            self.assertTrue(any('size:' in x for x in c.verify(p,root)['errors']))

    def test_file_checks_do_not_imply_visual_or_native_approval(self):
        p=c.plan(['x-article'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);Image.new('RGB',(2000,800)).save(root/p['assets'][0]['path'])
            r=c.verify(p,root)
            self.assertTrue(r['fileChecksPassed'])
            self.assertTrue(r['visualPending']);self.assertTrue(r['nativePending'])

    def test_actual_crop_pixels_and_coordinates_are_verified(self):
        p=c.plan(['wechat-article']);a,b=p['assets']
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            main=Image.new('RGB',(1880,800),'navy');main.paste('orange',(40,0,840,800))
            main.save(root/a['path']);main.crop(b['cropBox']).save(root/b['path'])
            self.assertTrue(c.verify(p,root)['fileChecksPassed'])
            Image.new('RGB',(800,800),'white').save(root/b['path'])
            self.assertTrue(any('crop-source:' in x for x in c.verify(p,root)['errors']))
            main.crop(b['cropBox']).save(root/b['path'])
            b['cropNormalized']=[0,0,1,1]
            self.assertTrue(any('cropNormalized:' in x for x in c.verify(p,root)['errors']))

    def test_forged_independent_square_fails(self):
        p=c.plan(['wechat-article']);p['assets'][1]['kind']='generated'
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(any('独立生成图' in x for x in c.verify(p,Path(d))['errors']))

    def test_missing_slot_rejected(self):
        p=c.plan(['douyin']);p['placements'].pop()
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(any('missing slot' in x for x in c.verify(p,Path(d))['errors']))


if __name__=='__main__': unittest.main()
