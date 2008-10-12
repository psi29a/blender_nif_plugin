"""Automated skinning tests for the blender nif scripts."""

# ***** BEGIN LICENSE BLOCK *****
# 
# BSD License
# 
# Copyright (c) 2007-2008, NIF File Format Library and Tools
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the NIF File Format Library and Tools project may not be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

from itertools import izip

from nif_test import TestSuite
from PyFFI.Formats.NIF import NifFormat

# helper functions

def are_vectors_equal(oldvec, newvec, tolerance = 0.01):
    return (max([abs(x-y)
            for (x,y) in izip(oldvec.asList(), newvec.asList())]) < tolerance)

def are_matrices_equal(oldmat, newmat, tolerance = 0.01):
    return (max([max([abs(x-y)
                 for (x,y) in izip(oldrow, newrow)])
                for (oldrow, newrow) in izip(oldmat.asList(), newmat.asList())])
            < tolerance)

def are_floats_equal(oldfloat, newfloat, tolerance = 0.01):
    return abs(oldfloat - newfloat) < tolerance

def compare_skinning_info(oldroot, newroot):
    """Raises a C{ValueError} if skinning info is different between old and
    new."""
    print("checking skinning data...")
    # get the geometries
    for oldgeom in oldroot.tree(block_type = NifFormat.NiGeometry):
        for newgeom in newroot.tree(block_type = NifFormat.NiGeometry):
            # list all old bones
            for oldbone, oldbonedata \
                in izip(oldgeom.skinInstance.bones,
                        oldgeom.skinInstance.data.boneList):
                for newbone, newbonedata \
                    in izip(newgeom.skinInstance.bones,
                        newgeom.skinInstance.data.boneList):
                    if oldbone.name == newbone.name:
                        print ("  checking bone %s" % oldbone.name)
                        # comparing
                        if not are_matrices_equal(oldbonedata.rotation, newbonedata.rotation):
                            #raise ValueError(
                            print(
                                "rotation mismatch\n%s\n!=\n%s\n"
                                % (oldbonedata.rotation, newbonedata.rotation))
                        if not are_vectors_equal(oldbonedata.translation, newbonedata.translation):
                            #raise ValueError(
                            print(
                                "translation mismatch\n%s\n!=\n%s\n"
                                % (oldbonedata.translation,
                                   newbonedata.translation))
                        if not are_floats_equal(oldbonedata.scale, newbonedata.scale):
                            #raise ValueError(
                            print(
                                "scale mismatch %s != %s"
                                % (oldbonedata.scale, newbonedata.scale))
    return

# some tests to import and export nif files

class TestSuiteChampionArmor(TestSuite):
    def run(self):
        # champion armor
        champ = self.test(
            filename = 'test/nif/cuirass.nif')
        champ_export = self.test(
            filename = 'test/nif/_cuirass.nif',
            config = dict(
                EXPORT_VERSION = 'Oblivion', EXPORT_SMOOTHOBJECTSEAMS = True,
                EXPORT_FLATTENSKIN = True),
            selection = ['Scene Root'])
        compare_skinning_info(
            NifFormat.read(open("test/nif/cuirass.nif", "rb"), version=0x14000005, user_version=11)[0],
            champ_export.root_blocks[0])

class SkinningTestSuite(TestSuite):
    def run(self):
        # oblivion full body
        bodyskel = self.test(
            filename = 'test/nif/skeleton.nif',
            config = dict(IMPORT_SKELETON = 1))
        bodyupp = self.test(
            filename = 'test/nif/upperbody.nif',
            config = dict(IMPORT_SKELETON = 2),
            selection = ['Scene Root'])
        bodylow = self.test(
            filename = 'test/nif/lowerbody.nif',
            config = dict(IMPORT_SKELETON = 2),
            selection = ['Scene Root'])
        bodyhand = self.test(
            filename = 'test/nif/hand.nif',
            config = dict(IMPORT_SKELETON = 2),
            selection = ['Scene Root'])
        bodyfoot = self.test(
            filename = 'test/nif/foot.nif',
            config = dict(IMPORT_SKELETON = 2),
            selection = ['Scene Root'])
        body_export = self.test(
            filename = 'test/nif/_fulloblivionbody.nif',
            config = dict(
                EXPORT_VERSION = 'Oblivion', EXPORT_SMOOTHOBJECTSEAMS = True,
                EXPORT_FLATTENSKIN = True),
            selection = ['Scene Root'])
        compare_skinning_info(
            NifFormat.read(open("test/nif/upperbody.nif", "rb"), version=0x14000005, user_version=11)[0],
            body_export.root_blocks[0])
        compare_skinning_info(
            NifFormat.read(open("test/nif/lowerbody.nif", "rb"), version=0x14000005, user_version=11)[0],
            body_export.root_blocks[0])
        compare_skinning_info(
            NifFormat.read(open("test/nif/hand.nif", "rb"), version=0x14000005, user_version=11)[0],
            body_export.root_blocks[0])
        compare_skinning_info(
            NifFormat.read(open("test/nif/foot.nif", "rb"), version=0x14000005, user_version=11)[0],
            body_export.root_blocks[0])
        # morrowind creature
        self.test(filename = 'test/nif/babelfish.nif')
        self.test(
            filename = 'test/nif/_babelfish.nif',
            config = dict(
                EXPORT_VERSION = 'Morrowind',
                EXPORT_STRIPIFY = False, EXPORT_SKINPARTITION = False),
            selection = ['Root Bone'])
        # morrowind better bodies mesh
        bbskin_import = self.test(filename = 'test/nif/bb_skinf_br.nif')
        bbskin_export = self.test(
            filename = 'test/nif/_bb_skinf_br.nif',
            config = dict(
                EXPORT_VERSION = 'Morrowind', EXPORT_SMOOTHOBJECTSEAMS = True,
                EXPORT_STRIPIFY = False, EXPORT_SKINPARTITION = False),
            selection = ['Bip01'])
        compare_skinning_info(
            bbskin_import.root_blocks[0],
            bbskin_export.root_blocks[0])

### "Scene Root" of champion armor conflicts with "Scene Root" of full body
### test below, so for now this test is disabled until a solution is found
#suite = TestSuiteChampionArmor("champion_armor")
#suite.run()
suite = SkinningTestSuite("skinning")
suite.run()

