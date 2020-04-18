#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compute tract profiles and their statistics along streamlines.
"""


import argparse
import json
import os

import nibabel as nib
import numpy as np


from scilpy.io.streamlines import load_tractogram_with_reference
from scilpy.io.image import assert_same_resolution
from scilpy.io.utils import (assert_inputs_exist,
                             add_json_args,
                             add_overwrite_arg,
                             add_reference_arg)
from scilpy.utils.filenames import split_name_with_nii
from scilpy.utils.metrics_tools import get_bundle_metrics_profiles
from scilpy.tracking.tools import resample_streamlines_num_points
from scilpy.tractanalysis.features import get_streamlines_centroid


def norm_l2(x):
    return np.sqrt(np.sum(np.power(x, 2), axis=1, dtype=np.float32))


def average_euclidean(x, y):
    return np.mean(norm_l2(x - y))


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_bundle',
                   help='Fiber bundle file to compute the tract profiles on.')
    p.add_argument('in_metrics', nargs='+',
                   help='Nifti metric(s) on which to compute '
                        'the tract profiles.')
    p.add_argument('--in_centroid',
                   help='If provided it will be used to make sure all '
                        'streamlines go in the same direction. Otherwise, a '
                        'centroid will be automatically computed.')
    p.add_argument('--nb_pts_per_streamline',
                   type=int, default=20,
                   help='Subsample each streamline to this number of points.')

    add_json_args(p)
    add_reference_arg(p)
    add_overwrite_arg(p)
    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, [args.in_bundle] + args.in_metrics,
                        optional=args.in_centroid)

    if args.nb_pts_per_streamline <= 1:
        parser.error('--nb_pts_per_streamline {} needs to be greater than '
                     '1'.format(args.nb_pts_per_streamline))

    assert_same_resolution(args.in_metrics)
    metrics = [nib.load(m) for m in args.in_metrics]

    sft = load_tractogram_with_reference(parser, args, args.in_bundle)

    bundle_name, _ = os.path.splitext(os.path.basename(args.in_bundle))
    stats = {}
    if len(sft) == 0:
        stats[bundle_name] = None
        print(json.dumps(stats, indent=args.indent, sort_keys=args.sort_keys))
        return

    resampled_sft = resample_streamlines_num_points(sft,
                                                    args.nb_pts_per_streamline)

    # Centroid - will be use as reference to reorient each streamline
    if args.in_centroid:
        sft_centroid = load_tractogram_with_reference(parser, args,
                                                      args.in_centroid)
        centroid_streamlines = sft_centroid.streamlines
    else:
        centroid_streamlines = get_streamlines_centroid(resampled_sft.streamlines,
                                                        args.nb_pts_per_streamline)

    # Make sure all streamlines go in the same direction. We want to make
    # sure point #1 / args.nb_pts_per_streamline of streamline A is matched
    # with point #1 / 20 of streamline B and so on
    num_streamlines = len(resampled_sft.streamlines)

    for s in np.arange(num_streamlines):
        streamline = resampled_sft.streamlines[s]
        direct = average_euclidean(centroid_streamlines, streamline)
        flipped = average_euclidean(centroid_streamlines, streamline[::-1])

        if flipped < direct:
            resampled_sft.streamlines[s] = streamline[::-1]

    profiles = get_bundle_metrics_profiles(resampled_sft, metrics)
    t_profiles = np.expand_dims(profiles, axis=1)
    t_profiles = np.rollaxis(t_profiles, 3, 2)

    stats[bundle_name] = {}
    for metric, profile, t_profile in zip(metrics, profiles, t_profiles):
        metric_name, _ = split_name_with_nii(
            os.path.basename(metric.get_filename()))
        stats[bundle_name][metric_name] = {
            'mean': np.mean(profile, axis=0).tolist(),
            'std': np.std(profile, axis=0).tolist(),
            'tractprofile': t_profile.tolist()
        }

    print(json.dumps(stats, indent=args.indent, sort_keys=args.sort_keys))


if __name__ == '__main__':
    main()
