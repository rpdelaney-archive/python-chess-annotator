#python-chess-annotator
Takes a PGN file as an argument and annotates the first game in that file
using an engine.

The result will be printed on standard output (the file on disk will be
unchanged).

##Dependencies
You will need a UCI[[1]] chess engine for analysis. stockfish[[2]] is the
default.

Requires python-chess[[3]] by Niklas Fiekas:
```
pip install python-chess
```

##Usage
```
$ python annotator.py -h
usage: annotator.py [-h] --file FILE [--engine ENGINE] [--time TIME]
                    [--verbose]

optional arguments:
  -h, --help                 show this help message and exit
  --file FILE, -f FILE       input PGN file
  --engine ENGINE, -e ENGINE analysis engine (default: stockfish)
  --time TIME, -t TIME       minutes to spend on analysis (default: 1)
  --verbose, -v              increase verbosity (print debugging info)

$ python annotator.py -f caruana-kasparov.pgn -t 15
[Event "Ultimate Blitz Challenge"]
[Site "St. Louis, MO USA"]
[Date "2016.04.29"]
[Round "18.1"]
[White "Fabiano Caruana"]
[Black "Garry Kasparov"]
[Result "0-1"]
[EventDate "2016.04.28"]
[ECO "A05"]
[WhiteElo "2795"]
[BlackElo "2812"]
[PlyCount "74"]
[Opening "King's Indian Attack: Symmetrical Defense"]
[Annotator "Stockfish 7 64 POPCNT"]

{ Stockfish 7 64 POPCNT } 1. Nf3 Nf6 2. g3 g6 { A05 King's Indian Attack: Symmetrical Defense }
3. Bg2 Bg7 4. O-O O-O 5. c4 d6 6. b3 e5 7. Bb2 c5 8. e3 Nc6 9. Nc3 Bf5 10. d4 e4 11. Ne1 Re8
12. Nc2 h5 13. Qd2 h4 14. Ba3 $6 { -0.85 } ( 14. h3 { 0.26 } ) 14... b6 $6 { 0.29 } ( 14... Nh7
{ -0.84 } ) 15. Rfd1 $6 { -0.81 } ( 15. h3 { 0.00 } ) 15... Bg4 16. Rdc1 Qd7 17. b4 Qf5 18. Bb2
Rad8 19. Nb5 Bf3 20. d5 $6 { -2.59 } ( 20. Bf1 Qh5 { -1.58 } ) 20... Ne5 $6 { -1.18 }
( 20... Nxb4 { -2.62 } ) 21. Bxe5 Rxe5 22. Ne1 hxg3 23. fxg3 Bh6 24. Rab1 Kg7 { -0.83 }
( 24... Re7 25. Nc2 Qh5 26. bxc5 bxc5 27. h3 a6 28. Nc3 Qe5 29. Ne2 { -1.45 } ) 25. Rb3 Qh5
26. h3 Nh7 { -0.69 } ( 26... a6 { -1.24 } ) 27. g4 { -1.41 } ( 27. bxc5 bxc5 { -0.85 } )
27... Bxg4 28. hxg4 Qxg4 29. Qd1 $4 { -4.73 } ( 29. Qb2 Nf6 { -1.46 } ) 29... Qg3 30. Qe2 $6
{ -5.87 } ( 30. Nf3 exf3 { -4.85 } ) 30... Ng5 31. Kh1 $4 { Mate in 9 } ( 31. bxc5 Nh3+ { -7.50 } )
31... Rh8 32. Nxd6 Kg8 { -10.46 } ( 32... Nf3 33. Nf5+ Rxf5 34. Nxf3 Bxe3+ 35. Bh3 Rxh3+ 36. Nh2
Rxh2+ 37. Qxh2 { Mate in 7 } ) 33. bxc5 { Mate in 6 } ( 33. Kg1 Bf8 34. Nxe4 Nxe4 35. Qf3 Qh2+
36. Kf1 Nd2+ 37. Kf2 Qh4+ { -9.86 } ) 33... Bf8+ 34. Kg1 Nh3+ 35. Kf1 Bxd6 36. cxd6 { Mate in 9 }
( 36. Qc2 Rf5+ { -13.99 } ) 36... Rf5+ 37. Nf3 Rxf3+ 0-1
```

##To-do
- Reduce the frequency of annotations in positions where one side has an
  overwhelming advantage
- Don't truncate a PV that ends in mate
- Provide an option to analyze moves from one player only

##Legal
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

[1]: https://chessprogramming.wikispaces.com/UCI
[2]: https://stockfishchess.org/download/
[3]: https://github.com/niklasf/python-chess
<!-- vim: ft=markdown -->
