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

## From picture to FEN notation
In the picture below is an overview of the pipeline that an input picture goes through to be converted to FEN. Custom datasets were made to train models. **❗ Because of this we expect a significant performance drop on other types of chess boards, since our models/datasets are trained/created for one specific type of chess set ❗**

<p allign="center">
    <img src="https://github.com/MichielCreemers/ChessVision/blob/main/images/er_framework.png" />
</p>

### Corner Detection
Predicting the corners is done using a medium YOLOv8 object detection architecture, the dataset can be downloaded here: [corner-detection-dataset](https://universe.roboflow.com/chessar-c1hel/chess-board-detection-3jgw6). A pre-trained model can be downloaded here: [corners_best.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUTz1-GwVH9S7PBd?e=z4Oar3)

### Grid Segmentation
The grid segmentation is done using a small YOLOv8 segmentation architecture. Again a custom dataset for our own specific chess set was made for training and can be downloaded here: [grid-segmentation-dataset](https://universe.roboflow.com/chessar-c1hel/chess-board-detection-2). A pre-trained model can be downloaded here: [segment_grid.pt](https://1drv.ms/u/s!AtF_ruDO-AX-jiA2mkErqoB3VrHU?e=rlrAb1).

### Piece Detection
The piece detection is done by training both a large and nano YOLOv8 object detection architecture on a custom dataset that can be found here: [piece-detection-dataset](https://universe.roboflow.com/chessar-c1hel/chess_pieces_detection-7lqul). A pre-trained model can be downloaded here: [pieces_large.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUPtnTvaNnW-0rdN?e=6rK2Qc) or [pieces_nano.pt](https://1drv.ms/u/s!AtF_ruDO-AX-kUYP2Mp7a614Jh5J?e=Dv3fJ0).

### Overview of model performance
<table>
    <tr>
        <th> Model </th>
        <th> Inference time </th>
        <th> MAP50 </th>
        <th> MAP50-95 </th>
    </tr>
    <tr>
        <td> Corner Detection </td>
        <td> 30ms </td>
        <td> 90% </td>
        <td> 45% </td>
    </tr>
    <tr>
        <td> Grid Segmentation </td>
        <td> 20ms </td>
        <td> 99.8% </td>
        <td> 98% </td>
    </tr>
    <tr>
        <td> Piece Detection Large </td>
        <td> 35ms </td>
        <td> 98% </td>
        <td> 94% </td>
    </tr>
    <tr>
        <td> Piece Detection Nano </td>
        <td> 15ms </td>
        <td> 97% </td>
        <td> 94% </td>
    </tr>
</table>
Note the very small drop in precision when going from a large to a nano architecture for detecting the pieces, but a rather big drop in inference time. 

## Chess Engine
Once a valid FEN notation is computed, the Stockfish chess engine is used to determine the best move. This move is then plotted alongside the board configuration.

## Flask API
To communicate between the app and the API, Flask is used. This is micro framework that can receive GET and POST requests. As of now, it is set up to be hosted on the a laptop so that all devices on the same network can communicate with it. However, it can also be deployed on a server. To be able to connect to the API, the IP address has to be changed in the code of the file chessBot3\app\src\main\java\com\example\chessbot

<p allign="center">
    <img src="https://github.com/MichielCreemers/ChessVision/blob/main/images/test_images/chessvision.jpg" />
</p>

# Running the Code
Python version 3.11.7 is used. The dependancies can be installed by running:

```
pip install -r requirements.txt
```
Note that there might be some missing dependancies, I didn't use a specific environment for this project and I wouldn't want you to install 30GB of libraries 😁.

1. Start by placing the pre-trained models in the `models/` directory.
2. Dowload the Stockfish chess engine from https://stockfishchess.org/download/ and change the stockfish_path parameter in config.json to the location of the stockfish executable.
3. Configure the `config.json`:
   ```json
   {
    "pieces_model": "large",    # Choose between 'nano' and 'large'
    "piece_sampling": 10,       # Number of samples each piece bounding box is sampled
    "corner_conf": 0.15,
    "corner_iou": 0.1,
    "pieces_conf": 0.5,
    "pieces_iou": 0.35,
    "offsetx": 300,             # Offsets to make sure the whole pieces are visible after W1     
    "offsety": 300,
    "stockfish_path": "stockfish/stockfish-ubuntu-x86-64-avx2",  # Path to stockfish 
    "debug": "False"
    }
   ```
4. Run API
5. Change IP adress in app (see earlier: Flask API)


# Future Work
* All the jupyter notebooks are left in the main branch so you can experiment with them.
* As mentioned before, all the models are trained on a custom dataset for 1 specific chess board. Because of this we think the performance will drop if u try to use it with another chess set. 
  

- [ ] The datasets are linked in the discription, so we highly encourage you that expand our dataset and make the API usable for multiple chess sets.
- [ ] Board Orientation Detection ► Now just user input 
- [ ] If a picture is taken from a too large angle, the first transform will transform the picture so that white/black are left/right. This is illegal for FEN notation. In the file `board/grid.py` you can find a proof of concept function `correct_orientation_advanced()` that detects wheter the board is correctly orientated. This is not implemented in the API.
- [ ] The complete FEN notation requires parameters such as 'castling availability', 'en passant', 'half-move clock' and 'full-move number'. These are hardcoded as of right now because it was not our goal to make a chess app. The main focus was to make the 3D to 2D API.

