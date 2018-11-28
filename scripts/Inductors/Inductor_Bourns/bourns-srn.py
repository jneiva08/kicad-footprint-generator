#!/usr/bin/env python3
'''
kicad-footprint-generator is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
kicad-footprint-generator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
'''
import sys
import os
#sys.path.append(os.path.join(sys.path[0],"..","..","kicad_mod")) # load kicad_mod path
# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))  # load parent path of KicadModTree
from math import sqrt
import argparse
import yaml
#from helpers import *
from KicadModTree import *
sys.path.append(os.path.join(sys.path[0], "..", "..", "tools"))  # load parent path of tools
from footprint_text_fields import addTextFields

series = 'M20'
series_long = 'Female Vertical Surface Mount Double Row 2.54mm (0.1 inch) Pitch PCB Connector'
manufacturer = 'Harwin'
datasheet = 'https://cdn.harwin.com/pdfs/M20-781.pdf'
# https://cdn.harwin.com/pdfs/Harwin_Product_Catalog_page_225.pdf
pn = 'M20-781{n:02}45'
number_of_rows = 2
orientation = 'V'

pitch = 2.54
peg_drill_tht = 1.02
mount_drill = 1.8
pad_size = [1.78, 1.02]

#name, L, W, pad-w, pad-gap, pad-h
inductors = [
[1610,1.6,1.6,1.8,0.4,1.8],
[2010,2.0,1.6,2.3,0.6,1.9],
[2506,2.5,2.0,2.8,1.1,2.3],
[2508,2.5,2.0,2.8,1.1,2.3],
[2510,2.5,2.0,2.8,1.1,2.3],
[2512,2.5,2.0,2.8,1.1,2.3],
[3010,3.0,3.0,3.4,0.8,3.4],
[3012,3.0,3.0,3.4,0.8,3.4],
[3015,3.0,3.0,3.4,0.8,3.4],
[3020,3.0,3.0,3.5,0.8,3.4],
[4020,4.0,4.0,3.35,1.39,3.7],
]

def generate_footprint(array, configuration):

    mpn = pn.format(n=pins)
    pins_per_row = 2

    # handle arguments
    orientation_str = configuration['orientation_options'][orientation]
    footprint_name = configuration['fp_name_format_string'].format(man=manufacturer,
        series=series,
        mpn=mpn, num_rows=number_of_rows, pins_per_row=pins_per_row, mounting_pad = "",
        pitch=pitch, orientation=orientation_str)

    kicad_mod = Footprint(footprint_name)
    kicad_mod.setDescription("Harwin {:s}, {:s}, {:d} Pins per row ({:s}), generated with kicad-footprint-generator".format(series_long, mpn, pins_per_row, datasheet))
    kicad_mod.setTags(configuration['keyword_fp_string'].format(series=series,
        orientation=orientation_str, man=manufacturer,
        entry=configuration['entry_direction'][orientation]))

    kicad_mod.setAttribute('smd')

    ########################## Dimensions ##############################

    body_edge={
        'left': array[0],
        'right': array[1],
        'top': -2,
        'bottom': 2
    }

    ############################# Pads ##################################
    #
    # Add pads
    #
    #kicad_mod.append(PadArray(start=[-2.91, -B/2], initial=1,
    #    pincount=pins, increment=1,  y_spacing=pitch, size=pad_size,
    #    type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, layers=Pad.LAYERS_SMT))
    #kicad_mod.append(PadArray(start=[2.91, -B/2], initial=pins+1,
    #    pincount=pins, increment=1,  y_spacing=pitch, size=pad_size,
    #    type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, layers=Pad.LAYERS_SMT))

    ######################## Fabrication Layer ###########################
    main_body_poly= [
        {'x': body_edge['left'], 'y': body_edge['top']},
        {'x': body_edge['right'], 'y': body_edge['top']},
        {'x': body_edge['right'], 'y': body_edge['bottom']},
        {'x': body_edge['left'], 'y': body_edge['bottom']},
        {'x': body_edge['left'], 'y': body_edge['top']}
    ]
    #kicad_mod.append(PolygoneLine(polygone=main_body_poly,
    #    width=configuration['fab_line_width'], layer="F.Fab"))

    ######################## SilkS Layer ###########################
    poly_s_top= [
        {'x': body_edge['left'] - configuration['silk_fab_offset'], 'y': body_edge['top'] - configuration['silk_fab_offset'] + .7},
        {'x': body_edge['left'] - configuration['silk_fab_offset'], 'y': body_edge['top'] - configuration['silk_fab_offset']},
        {'x': body_edge['right'] + configuration['silk_fab_offset'], 'y': body_edge['top'] - configuration['silk_fab_offset']},
        {'x': body_edge['right'] + configuration['silk_fab_offset'], 'y': body_edge['top'] - configuration['silk_fab_offset'] + .7},
    ]
    #kicad_mod.append(PolygoneLine(polygone=poly_s_top,
    #    width=configuration['silk_line_width'], layer="F.SilkS"))

    poly_s_bot= [
        {'x': body_edge['left'] - configuration['silk_fab_offset'], 'y': body_edge['bottom'] + configuration['silk_fab_offset'] - .7},
        {'x': body_edge['left'] - configuration['silk_fab_offset'], 'y': body_edge['bottom'] + configuration['silk_fab_offset']},
        {'x': body_edge['right'] + configuration['silk_fab_offset'], 'y': body_edge['bottom'] + configuration['silk_fab_offset']},
        {'x': body_edge['right'] + configuration['silk_fab_offset'], 'y': body_edge['bottom'] + configuration['silk_fab_offset'] - .7},
    ]
    #kicad_mod.append(PolygoneLine(polygone=poly_s_bot,
    #    width=configuration['silk_line_width'], layer="F.SilkS"))

    ######################## CrtYd Layer ###########################
    CrtYd_offset = configuration['courtyard_offset']['connector']
    CrtYd_grid = configuration['courtyard_grid']

    poly_yd = [
        {'x': -3.8 - CrtYd_offset, 'y': body_edge['top'] - CrtYd_offset},
        {'x': 3.8 + CrtYd_offset, 'y': body_edge['top'] - CrtYd_offset},
        {'x': 3.8 + CrtYd_offset, 'y': body_edge['bottom'] + CrtYd_offset},
        {'x': -3.8 - CrtYd_offset, 'y': body_edge['bottom'] + CrtYd_offset},
        {'x': -3.8 - CrtYd_offset, 'y': body_edge['top'] - CrtYd_offset}
    ]

    #kicad_mod.append(PolygoneLine(polygone=poly_yd,
    #    layer='F.CrtYd', width=configuration['courtyard_line_width']))

    ######################### Text Fields ###############################
    cy1 = body_edge['top'] - configuration['courtyard_offset']['connector']
    cy2 = body_edge['bottom'] + configuration['courtyard_offset']['connector'] + 0.2

    #addTextFields(kicad_mod=kicad_mod, configuration=configuration, body_edges=body_edge,
    #    courtyard={'top':cy1, 'bottom':cy2}, fp_name=footprint_name, text_y_inside_position='top')

    ##################### Write to File and 3D ############################
    model3d_path_prefix = configuration.get('3d_model_prefix','${KISYS3DMOD}/')

    lib_name = configuration['lib_name_format_string'].format(series=series, man=manufacturer)
    #model_name = '{model3d_path_prefix:s}{lib_name:s}.3dshapes/{fp_name:s}.wrl'.format(
        model3d_path_prefix=model3d_path_prefix, lib_name=lib_name, fp_name=footprint_name)
    #kicad_mod.append(Model(filename=model_name))

    output_dir = '{lib_name:s}.pretty/'.format(lib_name=lib_name)
    if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
        os.makedirs(output_dir)
    filename =  '{outdir:s}{fp_name:s}.kicad_mod'.format(outdir=output_dir, fp_name=footprint_name)

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='use confing .yaml files to create footprints.')
    parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='../../tools/global_config_files/config_KLCv3.0.yaml')
    parser.add_argument('--series_config', type=str, nargs='?', help='the config file defining series parameters.', default='../conn_config_KLCv3.yaml')
    parser.add_argument('--kicad4_compatible', action='store_true', help='Create footprints kicad 4 compatible')
    args = parser.parse_args()

    with open(args.global_config, 'r') as config_stream:
        try:
            configuration = yaml.load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    with open(args.series_config, 'r') as config_stream:
        try:
            configuration.update(yaml.load(config_stream))
        except yaml.YAMLError as exc:
            print(exc)

    configuration['kicad4_compatible'] = args.kicad4_compatible

    for array in inductors:
        generate_footprint(array, configuration)

