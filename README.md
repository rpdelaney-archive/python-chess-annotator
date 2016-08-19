#python-chess-annotator

Takes a PGN files as an argument and annotates the first game in that file
using an engine.

The result will be printed on standard output (the file on disk will be
unchanged).

##Usage
```
usage: annotator.py [-h] --file FILE [--engine ENGINE] [--depth DEPTH]
                    [--verbose]

optional arguments:
  -h, --help					show the help message and exit
  --file FILE, -f FILE			input PGN file
  --engine ENGINE, -e ENGINE	analysis engine (default: stockfish)
  --depth DEPTH, -d DEPTH		search depth (default: 14)
  --verbose, -v					increase verbosity (print debugging info)
```

#Legal
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

<!-- vim: ft=markdown -->
