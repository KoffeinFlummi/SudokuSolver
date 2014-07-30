#!/usr/bin/python


# SUDOKU SOLVER
# Author: KoffeinFlummi
# Requires: 
#   - numpy
#   - OpenCV2
#   - An installation of tesseract

# DESCRIPTION
# Tries to extract a sudoku from an image and solve it.
# While it isn't always able to extract every digit from the
# given sudoku, that is usually enough to be able to solve it.

# USAGE
# Called from the command line with the filename of the image
# containing the sudoku as an argument, like so:
# $ python sudokusolver.py mysuperhardsudoku.jpg

# GETTING THE BEST RESULTS
# The script needs to be able to detect the shape of the sudoku,
# so please make sure that there's nothing but the sudoku in the
# picture and that the paper doesn't have any bends or creases
# in it that might make it harder to detect square shapes.


from __future__ import division

import sys
import os
import subprocess
import copy
import numpy as np

from cv2 import *

debug = False

def findFreeFilename(ext):
  """ Finds a free filename to store a temporary file under. """
  parent = os.path.realpath(__file__)
  for i in range(100):
    filename = "temp"+str(i)+"."+ext
    if not os.path.exists(os.path.join(parent, filename)):
      return filename
  return filename

def debugImage(img, name):
  """ Shows an image for debugging. """
  global debug
  if not debug:
    return None

  namedWindow(name)
  imshow(name, img)
  #imwrite(name+".jpg", img) # uncomment if you want to save the individual steps
  waitKey()

def printSudoku(su):
  """ Prints a sudoku thingy nicely. """
  print "+-------+-------+-------+"
  for i in range(9):
    string = "| "+str(su[i][0])+" "+str(su[i][1])+" "+str(su[i][2])+" | "+str(su[i][3])+" "+str(su[i][4])+" "+str(su[i][5])+" | "+str(su[i][6])+" "+str(su[i][7])+" "+str(su[i][8])+" |"
    print string.replace("0", " ")
    if i in [2,5,8]:
      print "+-------+-------+-------+"

def projectImage(img):
  """ Compensates for perspective by finding the outline and making the sudoku a square again. """
  global debug

  # Grayscale image for easier processing
  gray = cvtColor(img, COLOR_BGR2GRAY)
  canny = Canny(gray, 50, 200)

  debugImage(canny, "edgedetected")

  # Detect contours
  contours, hierarchy = findContours(canny, RETR_TREE, CHAIN_APPROX_SIMPLE)

  # Filter contours for things that might be squares
  squares = []
  for contour in contours:
    contour = approxPolyDP(contour, 0.02*arcLength(contour, True), True)
    if len(contour) == 4 and isContourConvex(contour):
      squares.append(contour)

  # Find the biggest one.
  squares = [sorted(squares, key=lambda x: contourArea(x))[-1]]
  squares[0] = squares[0].reshape(-1, 2)

  imgcontours = img
  drawContours(imgcontours, squares, -1, (0,0,255))
  debugImage(imgcontours, "squares")

  # Arrange the border points of the contour we found so that they match pointsNew.
  pointsOriginal = sorted(squares[0], key=lambda x: x[0])
  pointsOriginal[0:2] = sorted(pointsOriginal[0:2], key=lambda x: x[1])
  pointsOriginal[2:4] = sorted(pointsOriginal[2:4], key=lambda x: x[1])
  pointsOriginal = np.float32(pointsOriginal)
  pointsNew = np.float32([[0,0],[0,450],[450,0],[450,450]])

  # Warp the image to be a square.
  persTrans = getPerspectiveTransform(pointsOriginal, pointsNew)
  fixedImage = warpPerspective(img, persTrans, (450,450))

  debugImage(fixedImage, "perspectivefix")

  return fixedImage

def extractSudoku(img):
  """ Extracts the actual numbers from the image using tesseract. """
  global debug

  sudoku = []
  for i in range(9):
    sudoku_temp = []
    for j in range(9):
      border = 5 # how much to cut off the edges to eliminate any of the lines between the cells
      subimg = img[i*50+border:(i+1)*50-border, j*50+border:(j+1)*50-border]
      subimg = cvtColor(subimg, COLOR_BGR2RGB)
      ret,thresh = threshold(subimg,127,255,THRESH_BINARY) # black-and-white for most contrast

      tesinput = findFreeFilename("jpg")
      tesoutput = findFreeFilename("txt")
      imwrite(tesinput, thresh)

      try:
        subprocess.check_output("tesseract "+tesinput+" "+tesoutput[:-4]+" -psm 10", shell=True)
        digit = int(open(tesoutput, "r").read())
      except:
        digit = 0

      try:
        os.remove(tesinput)
        os.remove(tesoutput)
      except:
        print "Failed to delete temp files. Probably some bullshit with permissions."
        sys.exit(1)

      sudoku_temp.append(digit)
      sys.stdout.write("\r"+"Extracting data ... "+str(int((i*9+j+1)/81*100)).rjust(3)+"%")
      sys.stdout.flush()
    sudoku.append(sudoku_temp)

  return sudoku

def isValidSolution(sudoku):
  """ Checks if the given sudoku is a valid solution. """
  if len(sudoku) != 9:
    return False

  # Check rows
  for i in sudoku:
    if sorted(i) != [1,2,3,4,5,6,7,8,9]:
      return False

  # Check columns
  for i in range(9):
    temp = []
    for j in range(9):
      temp.append(sudoku[j][i])
    if sorted(temp) != [1,2,3,4,5,6,7,8,9]:
      return False

  # Check clusters
  for i in range(3):
    for j in range(3):
      temp = sudoku[i*3][j*3:j*3+3] + sudoku[i*3+1][j*3:j*3+3] + sudoku[i*3+2][j*3:j*3+3]
      if sorted(temp) != [1,2,3,4,5,6,7,8,9]:
        return False

  return True

def same_row(sudoku, i, j):
  return sudoku[i]
def same_column(sudoku, i, j):
  return [row[j] for row in sudoku]
def same_cluster(sudoku, i, j):
  return sudoku[i//3*3][j//3*3:j//3*3+3] + sudoku[i//3*3+1][j//3*3:j//3*3+3] + sudoku[i//3*3+2][j//3*3:j//3*3+3]
def solveSudoku(sudoku, toplevel=True):
  """ Solves the given sudoku with a simple backtrack; nothing fancy. """
  global debug

  solutions = []
  for i in range(9):
    for j in range(9):
      if sudoku[i][j] == 0:
        for k in range(1,10):
          if not (k in same_row(sudoku,i,j) or k in same_column(sudoku,i,j) or k in same_cluster(sudoku,i,j)):
            temp = copy.deepcopy(sudoku)
            temp[i][j] = k
            solution = solveSudoku(temp, False)
            if solution != None:
              solutions.append(solution)

          if toplevel:
            sys.stdout.write("\rCalculating solution ... "+str(k*10).rjust(3)+"%")
            sys.stdout.flush()

        for solution in solutions:
          if isValidSolution(solution):
            return solution
        return None

  if isValidSolution(sudoku):
    return sudoku
  return None

def main():
  if len(sys.argv) < 2:
    print "Please supply a path to an image file as an argument."
    sys.exit(1)
  img = imread(sys.argv[1], 1)

  # Resize the image to a more appropriate size
  if img.shape[0] > img.shape[1]:
    sizecoef = 800 / img.shape[0]
  else:
    sizecoef = 800 / img.shape[1]
  if sizecoef < 1:
    img = resize(img, (0,0), fx=sizecoef, fy=sizecoef)

  debugImage(img, "img")

  sys.stdout.write("Preparing image ...")
  sys.stdout.flush()
  if debug:
    projection = projectImage(img)
  else:
    try:
      projection = projectImage(img)
    except:
      print "\rPreparing image ... failed."
      sys.exit(1)
  print "\rPreparing image ... done."

  sys.stdout.write("Extracting data ...")
  sys.stdout.flush()
  if debug:
    sudoku = extractSudoku(projection)
  else:
    try:
      sudoku = extractSudoku(projection)
    except:
      print "\rExtracting data ... failed."
      sys.exit(1)
  print "\rExtracting data ... done."

  print ""
  printSudoku(sudoku)
  print ""

  sys.stdout.write("Calculating solution ...")
  sys.stdout.flush()
  if debug:
    solution = solveSudoku(sudoku)
  else:
    try:
      solution = solveSudoku(sudoku)
    except:
      print "\rCalculating solution ... failed."
      sys.exit(1)
  print "\rCalculating solution ... done."

  print ""
  printSudoku(solution)
  print ""


if __name__ == "__main__":
  main()
