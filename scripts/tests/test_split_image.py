#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile

from scilpy.io.fetcher import fetch_data, get_home, get_testing_files_dict

# If they already exist, this only takes 5 seconds (check md5sum)
fetch_data(get_testing_files_dict(), keys=['processing.zip'])
tmp_dir = tempfile.TemporaryDirectory()


def test_help_option(script_runner):
    ret = script_runner.run('scil_split_image.py', '--help')
    assert ret.success


def test_execution_processing_no_output_given(script_runner):
    os.chdir(os.path.expanduser(tmp_dir.name))
    in_dwi = os.path.join(get_home(), 'processing',
                          'dwi_crop.nii.gz')
    in_bval = os.path.join(get_home(), 'processing',
                           'dwi.bval')
    in_bvec = os.path.join(get_home(), 'processing',
                           'dwi.bvec')
    ret = script_runner.run('scil_split_image.py', in_dwi,
                            in_bval, in_bvec, '5', '15', '25')
    assert ret.success


def test_execution_processing_good_output_given(script_runner):
    os.chdir(os.path.expanduser(tmp_dir.name))
    in_dwi = os.path.join(get_home(), 'processing',
                          'dwi_crop.nii.gz')
    in_bval = os.path.join(get_home(), 'processing',
                           'dwi.bval')
    in_bvec = os.path.join(get_home(), 'processing',
                           'dwi.bvec')
    ret = script_runner.run('scil_split_image.py', in_dwi,
                            in_bval, in_bvec, '5', '15',
                            '--out_dwi', 'dwi0.nii.gz', 'dwi1.nii.gz',
                            'dwi2.nii.gz', '--out_bval', 'dwi0.bval',
                            'dwi1.bval', 'dwi2.bval', '--out_bvec',
                            'dwi0.bvec', 'dwi1.bvec', 'dwi2.bvec')
    assert ret.success


def test_execution_processing_wrong_output(script_runner):
    os.chdir(os.path.expanduser(tmp_dir.name))
    in_dwi = os.path.join(get_home(), 'processing',
                          'dwi_crop.nii.gz')
    in_bval = os.path.join(get_home(), 'processing',
                           'dwi.bval')
    in_bvec = os.path.join(get_home(), 'processing',
                           'dwi.bvec')
    ret = script_runner.run('scil_split_image.py', in_dwi,
                            in_bval, in_bvec, '5', '15',
                            '--out_dwi', 'dwi0.nii.gz', 'dwi1.nii.gz',
                            '--out_bval', 'dwi0.bval',
                            'dwi1.bval', 'dwi2.bval', '--out_bvec',
                            'dwi0.bvec', 'dwi1.bvec', 'dwi2.bvec')
    assert (not ret.success)

    ret = script_runner.run('scil_split_image.py', in_dwi,
                            in_bval, in_bvec, '5', '15',
                            '--out_dwi', 'dwi0.nii.gz', 'dwi1.nii.gz',
                            'dwi2.nii.gz', '--out_bval', 'dwi0.bval',
                            'dwi1.bval', '--out_bvec',
                            'dwi0.bvec', 'dwi1.bvec', 'dwi2.bvec')
    assert (not ret.success)

    ret = script_runner.run('scil_split_image.py', in_dwi,
                            in_bval, in_bvec, '5', '15',
                            '--out_dwi', 'dwi0.nii.gz', 'dwi1.nii.gz',
                            'dwi2.nii.gz', '--out_bval', 'dwi0.bval',
                            'dwi1.bval', 'dwi2.bval', '--out_bvec',
                            'dwi0.bvec', 'dwi1.bvec')
    assert (not ret.success)


def test_execution_processing_wrong_indices_given(script_runner):
    os.chdir(os.path.expanduser(tmp_dir.name))
    in_dwi = os.path.join(get_home(), 'processing',
                          'dwi_crop.nii.gz')
    in_bval = os.path.join(get_home(), 'processing',
                           'dwi.bval')
    in_bvec = os.path.join(get_home(), 'processing',
                           'dwi.bvec')
    ret = script_runner.run('scil_split_image.py', in_dwi,
                            in_bval, in_bvec, '5', '25', '15')
    assert (not ret.success)
