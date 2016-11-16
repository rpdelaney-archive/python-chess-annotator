#python-chess-annotator
Takes a PGN file as an argument and annotates the games in that file using an
engine.

Computes average centipawn loss (ACPL) for each side and stores it in the
header.

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
  --time MINUTES, -t MINUTES time to spend on each game (default: 1)
  --verbose, -v              increase verbosity (print debugging info)

$ python annotator.py -f byrne-fischer.pgn -t 15
[Event "Third Rosenwald Trophy"]
[Site "New York, NY USA"]
[Date "1956.10.17"]
[Round "8"]
[White "Donald Byrne"]
[Black "Robert James Fischer"]
[Result "0-1"]
[EventDate "1956.10.07"]
[ECO "A15"]
[WhiteElo "?"]
[BlackElo "?"]
[PlyCount "82"]
[Opening "English Opening: Anglo-Indian Defense, King's Indian Formation"]
[White ACPL "160"]
[Black ACPL "3"]
[Annotator "Stockfish 7 64 POPCNT"]

{ Stockfish 7 64 POPCNT } 1. Nf3 Nf6 2. c4 g6 { A15 English Opening:
Anglo-Indian Defense, King's Indian Formation } 3. Nc3 Bg7 4. d4 O-O 5. Bf4 d5
6. Qb3 dxc4 7. Qxc4 c6 8. e4 Nbd7 9. Rd1 Nb6 10. Qc5 Bg4 11. Bg5 $6 { -1.41 } (
11. Be2 Nfd7 12. Qa3 Bxf3 13. Bxf3 e5 14. dxe5 Qe8 15. O-O Nxe5 { 0.07/27 } )
11... Na4 12. Qa3 Nxc3 13. bxc3 Nxe4 14. Bxe7 Qb6 15. Bc4 Nxc3 16. Bc5 Rfe8+
17. Kf1 Be6 18. Bxb6 $4 { -6.31 } ( 18. Qxc3 Qxc5 19. dxc5 Bxc3 20. Bxe6 Rxe6
21. g3 b5 22. cxb6 axb6 { -1.62/29 } ) 18... Bxc4+ 19. Kg1 Ne2+ 20. Kf1 Nxd4+
21. Kg1 Ne2+ 22. Kf1 Nc3+ 23. Kg1 axb6 24. Qb4 Ra4 25. Qxb6 $2 { -8.53 } ( 25.
Qxa4 Nxa4 { -6.25/25 } ) 25... Nxd1 26. h3 $6 { -9.91 } ( 26. a3 Rxa3
{ -8.43/27 } ) 26... Rxa2 27. Kh2 Nxf2 28. Re1 $6 { -10.74 } ( 28. Qxb7 Bd5
{ -9.86/26 } ) 28... Rxe1 29. Qd8+ Bf8 30. Nxe1 Bd5 31. Nf3 $4 { -13.28 }
( 31. Qb8 Re2 { -10.25/25 } ) 31... Ne4 32. Qb8 b5 33. h4 $6 { -13.67 }
( 33. Nd4 Nd6 34. Kg1 Rxg2+ 35. Kf1 Rd2 36. Qa7 Ne4 37. Ke1 Ra2 { -12.71/25 } )
33... h5 34. Ne5 $4 { -61.84 } ( 34. Kh3 Kg7 { -18.96/26 } ) 34... Kg7 35. Kg1 $4
{ Mate in 9 } ( 35. Nxf7 Kxf7 { -58.32/34 } ) 35... Bc5+ 36. Kf1 Ng3+ 37. Ke1
Bb4+ 38. Kd1 Bb3+ 39. Kc1 Ne2+ 40. Kb1 Nc3+ 41. Kc1 Rc2# 0-1
```

##To-do
- Add support for chess960
- Consider adding a GUI using Gooey[[4]]
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
[4]: https://github.com/chriskiehl/Gooey
<!-- vim: ft=markdown -->
