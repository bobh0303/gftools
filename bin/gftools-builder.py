#!/usr/bin/env python3
# Copyright 2020 The Google Font Tools Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import os
import sys

from gftools.builder import GFBuilder
from gftools.builder import __doc__ as GFBuilder_doc

try:
    from gftools.builder.ninja import NinjaBuilder

    builder_class = NinjaBuilder
except ImportError as e:
    builder_class = GFBuilder



parser = argparse.ArgumentParser(
    description=("Build a font family"),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="#"*79 + "\n" + GFBuilder_doc,
)
parser.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="Show extra debugging information",
)
parser.add_argument("--family-name", help="Font family name")
parser.add_argument(
    "--no-autohint",
    action="store_true",
    default=False,
    help="Don't run ttfautohint on static TTFs",
)
parser.add_argument("--stylespace", help="Path to a statmake stylespace file")

parser.add_argument(
    "--no-clean-up",
    action="store_true",
    default=False,
    help="Do not remove temporary files (instance_ufos/)")

parser.add_argument("file", nargs="*", help="YAML build config file *or* source files")

parser.add_argument("--dump-config", type=str, help="Config file to generate")

args = parser.parse_args()

if len(args.file) == 0:
    # Try a few places to find one.
    possible_config_files = list(filter(os.path.exists, [
        "sources/builder.yaml",
        "sources/builder.yml",
        "sources/config.yaml",
        "sources/config.yml",
        "builder.yaml",
        "builder.yml",
        "config.yaml",
        "config.yml",
    ]))
    if len(possible_config_files) > 0:
        args.file = [possible_config_files[0]]
        print(f"""
No config file specified; found a potential one in {args.file[0]}.
If this is not correct, please specify a config file manually.
""", file=sys.stderr)
    else:
        parser.print_usage()
        print("No config file specified")
        sys.exit(1)

if len(args.file) == 1 and (
    args.file[0].endswith(".yaml") or args.file[0].endswith(".yml")
):
    builder_args = dict(configfile=args.file[0])
else:
    config={"sources": args.file}
    if args.stylespace:
        config["stylespaceFile"] = args.stylespace
    if args.family_name:
        config["familyName"] = args.family_name
    builder_args = dict(config=config)

builder = builder_class(**builder_args)

if args.no_autohint:
    builder.config["autohintTTF"] = False

if args.no_clean_up:
    builder.config["cleanUp"] = False

if args.debug:
    builder.config["logLevel"] = "DEBUG"

if args.dump_config:
    import sys
    import yaml

    with open(args.dump_config, "w") as fp:
        config= {k: v for (k, v) in builder.config.items() if v is not None}
        fp.write(yaml.dump(config, Dumper=yaml.SafeDumper))
    sys.exit()

try:
    builder.build()
except NotImplementedError:
    builder = GFBuilder(**builder_args)
    builder.build()
