SudokuSolver
============

Tries to extract a sudoku from an image and solve it using a simple backtracking algorithm. While it isn't always able to extract every digit from the given sudoku, that is usually enough to be able to solve it.

### Requirements: 
- numpy
- OpenCV2
- An installation of tesseract

### Usage  
Called from the command line with the filename of the image containing the sudoku as an argument, like so:
```
$ python sudokusolver.py mysuperhardsudoku.jpg
```

If you want to test it out, feel free to use the sample image I provided (which is some picture I found on Google Images - If you're the owner of that picture and want it taken down, message me). If all goes well, you should see something like this:
```
$ python sudokusolver.py sample.jpg
Preparing image ... done.
Extracting data ... done.

+-------+-------+-------+
| 8     |   1   |     9 |
|   5   |     7 |   1   |
|     4 |   9   | 7     |
+-------+-------+-------+
|   6   | 7   1 |   2   |
| 5   8 |   6   | 1   7 |
|   1   | 5   2 |   9   |
+-------+-------+-------+
|     7 |   4   | 6     |
|   8   | 3   9 |   4   |
| 3     |   5   |     8 |
+-------+-------+-------+

Calculating solution ... done.

+-------+-------+-------+
| 8 7 2 | 4 1 3 | 5 6 9 |
| 9 5 6 | 8 2 7 | 3 1 4 |
| 1 3 4 | 6 9 5 | 7 8 2 |
+-------+-------+-------+
| 4 6 9 | 7 3 1 | 8 2 5 |
| 5 2 8 | 9 6 4 | 1 3 7 |
| 7 1 3 | 5 8 2 | 4 9 6 |
+-------+-------+-------+
| 2 9 7 | 1 4 8 | 6 5 3 |
| 6 8 5 | 3 7 9 | 2 4 1 |
| 3 4 1 | 2 5 6 | 9 7 8 |
+-------+-------+-------+
```

As you can see, it missed a digit, but was still able to calculate the solution properly.

### Getting The Best Results  
The script needs to be able to detect the shape of the sudoku, so please make sure that there's nothing but the sudoku in the picture and that the paper doesn't have any bends or creases in it that might make it harder to detect square shapes.


