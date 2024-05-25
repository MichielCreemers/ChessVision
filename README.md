# ♟ ChessVision API ♟
<p allign="center">
    <img src="https://github.com/MichielCreemers/ChessAR/blob/main/images/ChessVisionLogo.png" />
</p>

## Motivation
Welcome to the ChessVision API, a powerful tool designed to transform the traditional chess experience into an interactive and analytical adventure. This project leverages deep learning object detection architectures and image processing techiniques to analyze photographs of chess boards.

Whether you're a hobbyist looking to analyze your game by saving a digital representation of you physical setup, or a developer seeking to integrate chess insights into your applications, ChessVision provides an easy-to-use API that can enrich your chess playing or analysis.

## Description of project
Currently the API is configured in a way to work together with an adroid app we made that can be downloaded here: [ChessBot.zip](https://1drv.ms/u/s!AtF_ruDO-AX-kUiOVJsi6ivtiKqd?e=LOjFOB).

<p allign="center">
    <img src="https://github.com/MichielCreemers/ChessAR/blob/main/images/appje.png" />
</p>
This is just one of the many usecases someone could use this API for.

# Framework
## From picture to FEN notation
In the picture below is an overview of the pipeline that an input picture goes through to be converted to FEN.

<p allign="center">
    <img src="https://github.com/MichielCreemers/ChessAR/blob/main/images/er_framework.png" />
</p>

## Flask API


## To Do / Done
 - [x] Corner Detection
 - [x] Make Grid
 - [x] Get correct board orientation ❗Very primitive, can be made way more robust ► Check in `board/grid.py` the method `correct_orientation_advanced`❗
 - [X] Label chess pieces
 - [X] Train chess piece recognition model
 - [X] Map detected pieces to grid
 - [X] Output to FEN notation
 - [X] Best move
 - [X] Running API communication 
 - [X] App

## Pre-trained models
Pre-trained models can be downloaded here:
* Detecting the corners of the board: [corners.pt](https://1drv.ms/u/s!AtF_ruDO-AX-jhIXY82GK4tqbrni?e=OY8b9s)
* Detecting the corners of the board: [corners2.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUTz1-GwVH9S7PBd?e=z4Oar3)
* Detecting the corners of the board: [corners_best.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUTz1-GwVH9S7PBd?e=z4Oar3)
* Segmenting the tiles: [segment_grid.pt](https://1drv.ms/u/s!AtF_ruDO-AX-jiA2mkErqoB3VrHU?e=rlrAb1)
* Detecting Pieces on Board: [pieces_large.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUPtnTvaNnW-0rdN?e=6rK2Qc)
* Detecting Pieces on Board: [pieces_nano.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUYP2Mp7a614Jh5J?e=Dv3fJ0)
* Link to app: [ChessBot.zip](https://1drv.ms/u/s!AtF_ruDO-AX-kUiOVJsi6ivtiKqd?e=LOjFOB)


## Future Work
- [ ] Board Orientation Detection ► Now just user input 

