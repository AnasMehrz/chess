
import sys

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QPushButton, QSizePolicy, QVBoxLayout, \
    QLabel, QHBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400,400)
        global squares
        squares = self.initChessBoardGUI()
        self.displayMainMenu()
    def square(self, ID, grid_wid, row, column):
        ID = QPushButton(self)
        ID.clicked.connect(lambda: ChessPieces.movePiece(ChessPieces.active_piece, squares[7-row][column]))
        ID.setDisabled(True)
        grid_wid.addWidget(ID, row, column)
        ID.setFixedSize(self.size()/8)
        return ID

    def displayPromotion(self, pawn):
        promotion_bg = QWidget(self)
        promotion_bg.setStyleSheet('background-color: rgb(218, 219, 193);')
        promotion_bg.setGeometry(pawn.geometry())
        promotion_bg.setFixedSize(self.size().width()//6, self.size().height()//3)
        if self.geometry().y() - promotion_bg.geometry().y() < promotion_bg.size().height():
            promotion_bg.setGeometry(promotion_bg.geometry().x(), promotion_bg.geometry().y() - promotion_bg.size().height(), promotion_bg.width(), promotion_bg.height())

        promotion_menu = QVBoxLayout(promotion_bg)
        promotion_menu.setSpacing(0)

        banned_pieces = [Pawn, King]
        promotion_pieces = []
        buttons = []
        for piece in ChessPieces.pieces_dict:
            if type(piece) in banned_pieces:
                continue
            elif piece.piece_color == pawn.piece_color:
                promotion_pieces.append(piece)
                banned_pieces.append(type(piece))
        for piece in promotion_pieces:
            button = QPushButton()
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setIcon(piece.icon())
            button.setIconSize(button.size()/16)
            button.clicked.connect(lambda _,x=piece: ChessPieces.promote(pawn, type(x), promotion_bg))
            promotion_menu.addWidget(button)
            buttons.append(button)

        promotion_bg.show()

    def displayMainMenu(self):
        main_menu = QWidget(self)
        main_menu.setGeometry(self.geometry())
        main_menu.setStyleSheet(('background-color: blue;'))
        optionsWidget = QWidget(main_menu)
        optionsWidget.setGeometry(self.size().width()//3,self.size().height()//5 * 2, self.size().width()//3, self.size().height()//5)
        options = QVBoxLayout(optionsWidget)
        play = QPushButton('Play')
        play.clicked.connect(lambda: initGame(main_menu))
        pieces = QPushButton('Pieces')
        pieces.clicked.connect(lambda: pieceMenu(self, main_menu))
        options.addWidget(play)
        options.addWidget(pieces)
        main_menu.show()

    def initChessBoardGUI(self):
        global light_color
        global dark_color
        light_color = 'white'
        dark_color = 'brown'
        CHESS_SQUARES = [['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'],
                         ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
                         ['a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3'],
                         ['a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4'],
                         ['a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5'],
                         ['a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6'],
                         ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'],
                         ['a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8']]
        center = QWidget()
        self.setCentralWidget(center)
        grid = QGridLayout(center)
        grid.setSpacing(0)
        for column in range(8):
            for row in range(8):
                CHESS_SQUARES[row][column] = self.square(CHESS_SQUARES[row][column], grid, 7- row, column)
                if column % 2 == 0:
                    if row %2 == 0:
                        CHESS_SQUARES[row][column].setStyleSheet(f'background-color: {dark_color};')
                    else:
                        CHESS_SQUARES[row][column].setStyleSheet(f'background-color: {light_color};')
                else:
                    if row %2 == 0:
                        CHESS_SQUARES[row][column].setStyleSheet(f'background-color: {light_color};')
                    else:
                        CHESS_SQUARES[row][column].setStyleSheet(f'background-color: {dark_color};')
        return CHESS_SQUARES

class ChessPieces(QPushButton):
    active_piece = None
    last_active = None
    occupation_check_dict = {}
    pieces_dict = {}
    checkmate = False
    en_pass_pawn = None
    def __init__(self, current_square, piece_color):
        super().__init__(start_window)
        self.setIconSize(self.size())
        self.piece_color = piece_color
        self.sameKing = None
        self.setStyleSheet('background-color: rgba(0,0,0,0);')
        self.current_square = current_square
        ChessPieces.occupation_check_dict.update({self.current_square:self})
        ChessPieces.pieces_dict.update({self: self.piece_color})
        self.setGeometry(current_square.geometry())
        self.show()
        self.clicked.connect(self.activatePiece)
        for piece, color in self.pieces_dict.items():
            if isinstance(piece, King) and color == self.piece_color:
                self.sameKing = piece
                break

        self.clicked.connect(self.on_click)
    def promote(self, new_class, menu):

        ChessPieces.occupation_check_dict.pop(self.current_square)
        ChessPieces.pieces_dict.pop(self)
        promo_piece = new_class(self.current_square, self.piece_color)
        promo_piece.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.deleteLater()
        menu.deleteLater()

    def check_legal_moves(self):
        if not isinstance(self, King):


            moves = []
            for move in self.legal_moves:
                for row in self.sameKing.rows_block:
                    try:
                        if move not in row and ( move not in [piece.current_square for piece in self.sameKing.check_pieces] and len(self.sameKing.check_pieces) != 1):
                            move.setDisabled(True)

                        else:
                            move.setEnabled(True)
                            moves.append(move)
                            move.setStyleSheet('background-color: blue;')

                    except:
                        if move != row and (
                                move not in [piece.current_square for piece in self.sameKing.check_pieces] and len(
                                self.sameKing.check_pieces) != 1):
                            move.setDisabled(True)
                        else:
                            move.setEnabled(True)
                            moves.append(move)
                            move.setStyleSheet('background-color: blue;')
            self.original_color()
            return moves

    def on_click(self):
        if self.sameKing.check():
            self.get_legal_moves()
            self.check_legal_moves()

        else:
            self.get_legal_moves()

    def activatePiece(self):
        ChessPieces.last_active = ChessPieces.active_piece
        ChessPieces.active_piece = self
    def disableSquares(self):
        for row in squares:
            for square in row:
                square.setDisabled(True)
        self.original_color()
    def original_color(self):
        for row in squares:
            for square in row:
                if squares.index(row) % 2 == 0 and not square.isEnabled():
                    if row.index(square) % 2 == 0:
                        square.setStyleSheet(f'background-color: {dark_color};')
                    else:
                        square.setStyleSheet(f'background-color: {light_color};')
                elif squares.index(row) % 2 != 0 and not square.isEnabled():
                    if row.index(square) % 2 == 0:
                        square.setStyleSheet(f'background-color: {light_color};')
                    else:
                        square.setStyleSheet(f'background-color: {dark_color};')
    def movePiece(self, new_square):
        self.setGeometry(new_square.geometry())

        try:
            ChessPieces.capturePiece(self, new_square)
        except:
            pass
        self.disableSquares()
        ChessPieces.occupation_check_dict.pop(self.current_square, 'not found')
        self.current_square = new_square
        ChessPieces.occupation_check_dict.update({new_square:self})
        if not isinstance(self, King):
            counter = 0
            for row in self.sameKing.rows_block2:
                if new_square in row:
                    self.sameKing.safe_pieces.append(self)
                    break
                elif self in self.sameKing.safe_pieces and new_square not in row:
                    counter += 1
                    if counter == len(self.sameKing.rows_block2):
                        self.sameKing.safe_pieces.remove(self)
                        break

        if isinstance(self, King):
            if not self.moved:
                if self.castle_move1 != None:
                    if new_square == next(iter(self.castle_move1)):
                        ChessPieces.movePiece(self.castle_move1[new_square], squares[self.current_row_index][squares[self.current_row_index].index(new_square) - 1])
                if self.castle_move2 != None:
                    if new_square == next(iter(self.castle_move2)):
                        ChessPieces.movePiece(self.castle_move2[new_square], squares[self.current_row_index][squares[self.current_row_index].index(new_square) + 1])
        elif isinstance(self, Pawn):
            if self.piece_color == 'light':
                try:
                    if new_square in squares[self.row_index + 2]:
                        ChessPieces.en_pass_pawn = self
                except:
                    pass
            elif self.piece_color == 'dark':
                try:
                    if new_square in squares[self.row_index - 2]:
                        ChessPieces.en_pass_pawn = self
                except:
                    pass

            if new_square == self.en_pass_move and ChessPieces.occupation_check_dict.get(new_square):
                self.capturePiece(ChessPieces.en_pass_pawn.current_square)
                ChessPieces.occupation_check_dict.pop(ChessPieces.en_pass_pawn.current_square)

            for row in squares:
                if new_square in row and (squares.index(row) == 7 or squares.index(row) == 0):
                    MainWindow.displayPromotion(start_window, self)
                    break
        for key, value in ChessPieces.pieces_dict.items():

            if value == self.piece_color:
                key.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            else:
                key.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            if key == self and (isinstance(key, Rook) or isinstance(key, King)):
                key.moved = True
            if isinstance(key, King):
                if value != self.piece_color:
                    key.rows_block.clear()
                    key.check_pieces.clear()
                    if key.check():
                        key.get_legal_moves()
                        moves_enabled = False
                        for move in key.legal_moves:
                            if move.isEnabled():
                                moves_enabled = True
                                break
                        checkmate = None
                        for piece, color in ChessPieces.pieces_dict.items():
                            if (color == key.piece_color and piece.check_legal_moves() != [] and piece != key) or moves_enabled:
                                checkmate = False

                                break
                        self.disableSquares()
                        if checkmate == None:
                            checkmate == True
                            key.current_square.setStyleSheet('background-color: rgba(100,0,0,255);')
                            for piece in self.pieces_dict.keys():
                                piece.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                            break

    def capturePiece(self, square):
        piece = ChessPieces.occupation_check_dict.get(square)
        ChessPieces.pieces_dict.pop(piece)
        piece.setParent(None)
        piece.deleteLater()

class Pawn(ChessPieces):
    def __init__(self, position, pawn_color):
        super().__init__(position, pawn_color)
        self.start_square = position
        self.pawn_color = pawn_color
        self.legal_moves = []
        self.row_index = None
        self.en_pass_move = None

        if self.pawn_color == 'light':
            pawn_pixmap = QPixmap('pieceImages/pawn_white')
        else:
            pawn_pixmap = QPixmap('pieceImages/pawn_black')
        pawn_icon = QIcon(pawn_pixmap)
        self.setIcon(pawn_icon)

    def get_legal_moves(self):
        current_row_index = 0
        super().disableSquares()
        adj_diagonal1 = None
        adj_diagonal2 = None
        legal_moves = []
        for row in squares:
            if self.current_square in row:
                current_row_index = squares.index(row)
        self.row_index = current_row_index
        if self.pawn_color == 'light':
            if self.current_square == self.start_square:
                legal_moves = [squares[2][squares[1].index(self.current_square)],
                               squares[3][squares[1].index(self.current_square)]]
            else:
                try:
                    legal_moves = [squares[current_row_index + 1][squares[current_row_index].index(self.current_square)]]
                except:
                    pass
            try:
                if squares[current_row_index].index(self.current_square) - 1 >= 0:
                    adj_diagonal1 = squares[current_row_index + 1][squares[current_row_index].index(self.current_square) - 1]
            except:
                pass
            try:

                adj_diagonal2 = squares[current_row_index + 1][squares[current_row_index].index(self.current_square) + 1]
            except:
                pass

        elif self.pawn_color == 'dark':
            if self.current_square == self.start_square:
                legal_moves = [squares[5][squares[6].index(self.current_square)],
                               squares[4][squares[6].index(self.current_square)]]
            else:
                try:
                    legal_moves = [squares[current_row_index - 1][squares[current_row_index].index(self.current_square)]]
                except:
                    pass
            try:
                adj_diagonal1 = squares[current_row_index - 1][squares[current_row_index].index(self.current_square) - 1]
            except:
                pass
            try:
                adj_diagonal2 = squares[current_row_index - 1][squares[current_row_index].index(self.current_square) + 1]
            except:
                pass

        for i in legal_moves:
            if i in super().occupation_check_dict:
                legal_moves.remove(i)
        try:
            if super().occupation_check_dict.get(adj_diagonal1).piece_color != self.pawn_color and  super().occupation_check_dict.get(adj_diagonal1) != None:
                legal_moves.append(adj_diagonal1)
        except:
            pass
        try:
            if super().occupation_check_dict.get(adj_diagonal1).piece_color != self.pawn_color and type(super().occupation_check_dict.get(adj_diagonal1)) == King and super().occupation_check_dict.get(adj_diagonal1).piece_color != self.piece_color:
                super().occupation_check_dict.get(adj_diagonal1).rows_block.append(adj_diagonal1)
                super().occupation_check_dict.get(adj_diagonal1).check_pieces.append(self)

        except:
            pass
        try:
            if super().occupation_check_dict.get(adj_diagonal2).piece_color != self.pawn_color and  super().occupation_check_dict.get(adj_diagonal2) != None:
                    legal_moves.append(adj_diagonal2)
        except:
            pass
        try:

            if super().occupation_check_dict.get(adj_diagonal2).piece_color != self.pawn_color and type(super().occupation_check_dict.get(adj_diagonal2)) == King and super().occupation_check_dict.get(adj_diagonal2).piece_color != self.piece_color:
                super().occupation_check_dict.get(adj_diagonal2).rows_block.append(adj_diagonal2)
                super().occupation_check_dict.get(adj_diagonal2).check_pieces.append(self)




        except:
            pass
        try:
            if super().en_pass_pawn.current_square == squares[current_row_index][squares[current_row_index].index(self.current_square) - 1] and super().last_active == super().en_pass_pawn and super().en_pass_pawn. piece_color != self.piece_color:
                legal_moves.append(adj_diagonal1)
                self.en_pass_move = adj_diagonal1
        except:
            pass
        try:
            if super().en_pass_pawn.current_square == squares[current_row_index][squares[current_row_index].index(self.current_square) + 1] and super().last_active == super().en_pass_pawn and super().en_pass_pawn. piece_color != self.piece_color:
                legal_moves.append(adj_diagonal2)
                self.en_pass_move = adj_diagonal2
        except:
            pass

        for move in legal_moves:
            move.setEnabled(True)
            move.setStyleSheet('background-color: blue;')
        self.legal_moves = legal_moves

class Elephant(ChessPieces):
    def __init__(self, position, elephant_color):
        super().__init__(position, elephant_color)
        self.start_square = position
        self.elephant_color = elephant_color
        self.legal_moves = []
        elephant_pixmap = QPixmap('pieceImages/pawn_black')
        elephant_icon = QIcon(elephant_pixmap)
        self.setIcon(elephant_icon)
    def get_legal_moves(self):
        super().disableSquares()
        legal_moves = []
        save1 = []
        save2 = []
        save3 = []
        save4 = []
        legal_moves_copy = []
        counter_front1 = 1
        counter_back1 = 1


        row_index = None
        square_index = None
        for row in squares:
            for square in row:
                if square == self.current_square:
                    row_index = squares.index(row)
                    square_index = squares[row_index].index(square)

        for row in squares[row_index + 1:]:

            try:
                save1.append(squares[squares.index(row)][square_index + counter_front1])
                counter_front1 += 1
            except:
                pass
            if counter_back1 <= square_index:
                try:
                    save2.append(squares[squares.index(row)][square_index - counter_back1])
                    counter_back1 += 1
                except:
                    pass
        legal_moves.append(save1)
        legal_moves.append(save2)
        for row in squares[:row_index]:
            try:
                save3.append(squares[squares.index(row)][square_index + (row_index - squares.index(row))])

            except:
                pass
            if square_index - (row_index - squares.index(row)) >= 0:
                try:
                    save4.append(squares[squares.index(row)][square_index - (row_index - squares.index(row))])

                except:
                    pass
        save3 = list(reversed(save3))
        save4 = list(reversed(save4))
        legal_moves.append(save3)
        legal_moves.append(save4)
        for move_row in legal_moves:
            for move in move_row:
                move_index = move_row.index(move)
                if not move in super().occupation_check_dict or super().occupation_check_dict.get(move) == None:
                    continue

                elif self.elephant_color != super().occupation_check_dict.get(move).piece_color:
                    if isinstance(super().occupation_check_dict.get(move), King):
                        super().occupation_check_dict.get(move).rows_block.append(move_row.copy())
                        super().occupation_check_dict.get(move).check_pieces.append(self)
                    for i in move_row:
                        if isinstance(super().occupation_check_dict.get(i),King) and super().occupation_check_dict.get(i).piece_color != self.piece_color:
                            danger_row = move_row.copy()
                            danger_row.insert(0, self.current_square)
                            super().occupation_check_dict.get(i).rows_block2.append(danger_row[:danger_row.index(super().occupation_check_dict.get(i).current_square)])

                            break

                    for x in range(move_index, len(move_row)):
                        try:
                            move_row.pop(move_index + 1)
                        except:
                            pass
                else:
                    for x in range(move_index, len(move_row)):
                        move_row.pop(move_index)
                break
        for row in legal_moves:
            for move in row:
                move.setEnabled(True)
                move.setStyleSheet('background-color: blue;')
                legal_moves_copy.append(move)
        self.legal_moves = legal_moves_copy
    def discover_check(self, legal_moves):

         for piece, color in ChessPieces.pieces_dict.items():
             if color != self.piece_color and not isinstance(piece, King):
                 piece.get_legal_moves()
         self.disableSquares()

         for danger_row in self.sameKing.rows_block2:
             if self.current_square in danger_row:
                 for row in legal_moves:
                     for move in row:
                         if move not in danger_row:
                             try:
                                 row.remove(move)

                             except:
                                 pass

class Rook(ChessPieces):
    def __init__(self, position, rook_color):
        super().__init__(position, rook_color)
        self.start_square = position
        self.rook_color = rook_color
        self.legal_moves = []
        self.moved = False
        if self.rook_color == 'light':
            rook_pixmap = QPixmap('pieceImages/rook_white')
        else:
            rook_pixmap = QPixmap('pieceImages/rook_black')
        rook_icon = QIcon(rook_pixmap)
        self.setIcon(rook_icon)

    def get_legal_moves(self):
        self.legal_moves.clear()
        super().disableSquares()
        legal_moves = []
        save_fw = []
        save_bk = []
        save_left = []
        save_right = []
        legal_moves_copy = []
        row_index = None
        square_index = None
        for row in squares:
            for square in row:
                if square == self.current_square:
                    row_index = squares.index(row)
                    square_index = squares[row_index].index(square)
        for row in squares[row_index + 1:]:
            save_fw.append(row[square_index])
        for row in squares[:row_index]:
            save_bk.append(row[square_index])
        for square in squares[row_index][:square_index]:
            save_left.append(square)
        for square in squares[row_index][square_index + 1:]:
            save_right.append(square)
        legal_moves.append(save_fw)
        legal_moves.append(list(reversed(save_bk)))
        legal_moves.append(save_right)
        legal_moves.append(list(reversed(save_left)))
        for move_row in legal_moves:
            for move in move_row:
                move_index = move_row.index(move)
                if not move in super().occupation_check_dict or super().occupation_check_dict.get(move) == None:
                    continue
                elif self.rook_color != super().occupation_check_dict.get(move).piece_color:
                    if isinstance(super().occupation_check_dict.get(move), King):
                        super().occupation_check_dict.get(move).rows_block.append(move_row.copy())
                        super().occupation_check_dict.get(move).check_pieces.append(self)
                    for i in move_row:
                        if isinstance(super().occupation_check_dict.get(i),King) and super().occupation_check_dict.get(i).piece_color != self.piece_color:
                            danger_row = move_row.copy()
                            danger_row.insert(0, self.current_square)
                            super().occupation_check_dict.get(i).rows_block2.append(danger_row[:danger_row.index(super().occupation_check_dict.get(i).current_square)])

                            break

                    for x in range(move_index, len(move_row)):
                        try:
                            move_row.pop(move_index + 1)
                        except:
                            pass
                else:
                    for x in range(move_index, len(move_row)):
                        move_row.pop(move_index)

                break
        if super().active_piece == self:
            self.discover_check(legal_moves)
        for row in legal_moves:
            for move in row:
                move.setEnabled(True)
                move.setStyleSheet('background-color: blue;')
                legal_moves_copy.append(move)
        self.legal_moves = legal_moves_copy
    def discover_check(self, legal_moves):

         for piece, color in ChessPieces.pieces_dict.items():
             if color != self.piece_color and not isinstance(piece, King):
                 piece.get_legal_moves()
         self.disableSquares()

         for danger_row in self.sameKing.rows_block2:
             if self.current_square in danger_row:
                 for row in legal_moves:
                     for move in row:
                         if move not in danger_row:
                             try:
                                 row.remove(move)

                             except:
                                 pass

class Queen(ChessPieces):
    def __init__(self, position, queen_color):
        super().__init__(position, queen_color)
        self.legal_moves = []
        self.start_square = position
        self.queen_color = queen_color
        queen_pixmap = QPixmap('pieceImages/pawn_black')
        queen_icon = QIcon(queen_pixmap)
        self.setIcon(queen_icon)

    def get_legal_moves(self):
        super().disableSquares()
        self.legal_moves.clear()
        legal_moves = []
        save_fw = []
        save_bk = []
        save_left = []
        save_right = []
        save1 = []
        save2 = []
        save3 = []
        save4 = []
        legal_moves_copy = []
        counter_front1 = 1
        counter_back1 = 1


        row_index = None
        square_index = None
        for row in squares:
            for square in row:
                if square == self.current_square:
                    row_index = squares.index(row)
                    square_index = squares[row_index].index(square)
        for row in squares[row_index + 1:]:
            save_fw.append(row[square_index])
        for row in squares[:row_index]:
            save_bk.append(row[square_index])
        for square in squares[row_index][:square_index]:
            save_left.append(square)
        for square in squares[row_index][square_index + 1:]:
            save_right.append(square)
        legal_moves.append(save_fw)
        legal_moves.append(list(reversed(save_bk)))
        legal_moves.append(save_right)
        legal_moves.append(list(reversed(save_left)))

        for row in squares[row_index + 1:]:

            try:
                save1.append(squares[squares.index(row)][square_index + counter_front1])
                counter_front1 += 1
            except:
                pass
            if counter_back1 <= square_index:
                try:
                    save2.append(squares[squares.index(row)][square_index - counter_back1])
                    counter_back1 += 1
                except:
                    pass
        legal_moves.append(save1)
        legal_moves.append(save2)
        for row in squares[:row_index]:
            try:
                save3.append(squares[squares.index(row)][square_index + (row_index - squares.index(row))])

            except:
                pass
            if square_index - (row_index - squares.index(row)) >= 0:
                try:
                    save4.append(squares[squares.index(row)][square_index - (row_index - squares.index(row))])

                except:
                    pass
        save3 = list(reversed(save3))
        save4 = list(reversed(save4))
        legal_moves.append(save3)
        legal_moves.append(save4)

        for move_row in legal_moves:
            for move in move_row:
                move_index = move_row.index(move)
                if not move in super().occupation_check_dict or super().occupation_check_dict.get(move) == None:
                    continue
                elif self.queen_color != super().occupation_check_dict.get(move).piece_color:
                    if isinstance(super().occupation_check_dict.get(move), King):
                        super().occupation_check_dict.get(move).rows_block.append(move_row.copy())
                        super().occupation_check_dict.get(move).check_pieces.append(self)
                    for i in move_row:
                        if isinstance(super().occupation_check_dict.get(i), King) and super().occupation_check_dict.get(i).piece_color != self.piece_color:
                            danger_row = move_row.copy()
                            danger_row.insert(0, self.current_square)
                            super().occupation_check_dict.get(i).rows_block2.append(danger_row[:danger_row.index(super().occupation_check_dict.get(i).current_square)])

                            break
                    for x in range(move_index, len(move_row)):

                        try:
                            move_row.pop(move_index + 1)
                        except:
                            pass

                else:

                    for x in range(move_index, len(move_row)):
                        move_row.pop(move_index)
                break

        if ChessPieces.active_piece == self:
            self.discover_check(legal_moves)

        for row in legal_moves:
            for move in row:
                move.setEnabled(True)
                move.setStyleSheet('background-color: blue;')
                legal_moves_copy.append(move)


        self.legal_moves = legal_moves_copy
    def discover_check(self, legal_moves):

         for piece, color in ChessPieces.pieces_dict.items():
             if color != self.piece_color and not isinstance(piece, King):
                 piece.get_legal_moves()
         self.disableSquares()

         for danger_row in self.sameKing.rows_block2:
             if self.current_square in danger_row:
                 for row in legal_moves:
                     for move in row:
                         if move not in danger_row:
                             try:
                                 row.remove(move)

                             except:
                                 pass

class Horse(ChessPieces):

    def __init__(self, position, horse_color):
        super().__init__(position, horse_color)
        self.start_square = position
        self.horse_color = horse_color
        self.legal_moves = []
        if self.horse_color == 'light':
            horse_pixmap = QPixmap('pieceImages/horse_white')
        else:
            horse_pixmap = QPixmap('pieceImages/horse_black')
        horse_icon = QIcon(horse_pixmap)
        self.setIcon(horse_icon)

    def get_legal_moves(self):
        super().disableSquares()
        legal_moves = []
        row_index = None
        square_index = None
        for row in squares:
            for square in row:
                if square == self.current_square:
                    row_index = squares.index(row)
                    square_index = squares[row_index].index(square)

        try:
            legal_moves.append(squares[row_index + 2][square_index + 1])
        except:
            pass
        if square_index - 1 >= 0:
            try:
                legal_moves.append(squares[row_index + 2][square_index - 1])
            except:
                pass
        try:
            legal_moves.append(squares[row_index + 1][square_index + 2])
        except:
            pass
        if square_index - 2 >= 0:
            try:
                legal_moves.append(squares[row_index + 1][square_index - 2])
            except:
                pass
        if row_index - 1 >= 0:
            try:
                legal_moves.append(squares[row_index - 1][square_index + 2])
            except:
                pass
            if square_index - 2 >= 0:

                legal_moves.append(squares[row_index - 1][square_index - 2])

        if row_index - 2 >= 0:
            try:
                legal_moves.append(squares[row_index - 2][square_index + 1])
            except:
                pass
            if square_index - 1 >= 0:
                legal_moves.append(squares[row_index - 2][square_index - 1])
        if ChessPieces.active_piece == self:
            self.discover_check(legal_moves)
        for move in legal_moves:
            try:
                if super().occupation_check_dict.get(move).piece_color != self.horse_color:
                    move.setEnabled(True)
                    move.setStyleSheet('background-color: blue;')
            except:
                move.setEnabled(True)
                move.setStyleSheet('background-color: blue;')
        for move in legal_moves:
            if isinstance(super().occupation_check_dict.get(move), King):
                super().occupation_check_dict.get(move).check_pieces.append(self)
                super().occupation_check_dict.get(move).rows_block.append(move)
        self.legal_moves = legal_moves
    def discover_check(self, legal_moves):

         for piece, color in ChessPieces.pieces_dict.items():
             if color != self.piece_color and not isinstance(piece, King):
                 piece.get_legal_moves()
         self.disableSquares()

         for danger_row in self.sameKing.rows_block2:
             if self.current_square in danger_row:
                 for move in legal_moves:
                    if move not in danger_row:
                        try:
                            legal_moves.remove(move)

                        except:
                            pass

class King(ChessPieces):
    def __init__(self, position, king_color):
        super().__init__(position, king_color)
        self.start_square = position
        self.king_color = king_color
        self.rows_block = []
        self.rows_block2 = []
        self.check_pieces = []
        self.safe_pieces = []
        self.legal_moves = []
        self.legal_moves_improper = []

        self.current_row_index = None
        self.castle_move1 = None
        self.castle_move2 = None
        self.moved = False
        if self.piece_color == 'light':
            king_pixmap = QPixmap('pieceImages/king_white')
        else:
            king_pixmap = QPixmap('pieceImages/king_black')

        king_icon = QIcon(king_pixmap)
        self.setIcon(king_icon)
        self.clicked.connect(self.get_legal_moves)
    def get_legal_moves(self):
        super().disableSquares()
        legal_moves = []
        removed_moves = []
        castle_moves = []
        row_index = None
        square_index = None
        self.legal_moves_improper.clear()
        self.legal_moves.clear()
        for row in squares:
            for square in row:
                if square == self.current_square:
                    row_index = squares.index(row)
                    self.current_row_index = row_index
                    square_index = squares[row_index].index(square)
        for i in range (-1, 2):
            if row_index + i >= 0:
                try:
                    legal_moves.append(squares[row_index + i][square_index])
                    if square_index - 1 >= 0:
                        legal_moves.append(squares[row_index + i][square_index - 1])

                    try:
                        legal_moves.append(squares[row_index + i][square_index + 1])
                    except:
                        pass
                except:
                    pass

        for piece, color in super().pieces_dict.items():
            if isinstance(piece, Rook) and color == self.piece_color and not self.moved and not self.check():
                if not piece.moved and squares[row_index].index(piece.current_square) > square_index:
                    castle_moves.append(squares[row_index][square_index + 2])
                    self.castle_move1 = {squares[row_index][square_index + 2]:piece}
                    for row in self.rows_block:
                        if squares[row_index][square_index + 1] in row:
                                castle_moves.remove(squares[row_index][square_index + 2])
                                self.castle_move1 = None
                                break
                    for square in squares[row_index][square_index + 1:squares[row_index].index(piece.current_square)]:
                        if super().occupation_check_dict.get(square) != None:
                            castle_moves.remove(squares[row_index][square_index + 2])
                            self.castle_move1 = None
                            break
                elif not piece.moved:
                    castle_moves.append(squares[row_index][square_index - 2])
                    self.castle_move2 = {squares[row_index][square_index - 2]:piece}
                    for row in self.rows_block:
                        if squares[row_index][square_index - 1] in row:
                            castle_moves.remove(squares[row_index][square_index - 2])
                            self.castle_move2 = None
                            break
                    for square in squares[row_index][squares[row_index].index(piece.current_square) + 1:square_index]:
                        if super().occupation_check_dict.get(square) != None:
                            castle_moves.remove(squares[row_index][square_index - 2])
                            self.castle_move2 = None
                            break

        for move in castle_moves:
            legal_moves.append(move)

        for move in legal_moves:
            for piece, color  in super().pieces_dict.items():
                if piece == self:
                    continue
                elif isinstance(piece, King):
                    piece.king_legal_moves()
                    if move in piece.legal_moves:
                        removed_moves.append(move)
                elif color != self.piece_color:
                    piece.get_legal_moves()
                    if move in piece.legal_moves:
                        removed_moves.append(move)
                        break
            for row in self.rows_block:
                try:
                    for move in row:
                        removed_moves.append(move)
                except:
                    removed_moves.append(row)

        for move in removed_moves:
            if move in legal_moves:
                legal_moves.remove(move)
        super().disableSquares()
        for move in legal_moves:
            try:
                if super().occupation_check_dict.get(move).piece_color != self.king_color:
                    move.setEnabled(True)
                    move.setStyleSheet('background-color: blue;')
            except:
                if super().occupation_check_dict.get(move) == None:
                    move.setEnabled(True)
                    move.setStyleSheet('background-color: blue;')
                else:
                    pass
        for move in legal_moves:
            self.legal_moves.append(move)



    def check(self):
        for piece, color in super().pieces_dict.items():
            if piece == self:
                continue
            elif isinstance(piece, King):
                piece.king_legal_moves()

            elif self.piece_color != color:
                piece.get_legal_moves()
            super().disableSquares()
            if self.current_square in piece.legal_moves and color != self.piece_color:
                return True
        return False
    def king_legal_moves(self):
        legal_moves = []
        row_index = None
        square_index = None
        self.legal_moves_improper.clear()
        for row in squares:
            for square in row:
                if square == self.current_square:
                    row_index = squares.index(row)
                    square_index = squares[row_index].index(square)
        for i in range(-1, 2):
            if row_index + i >= 0:
                try:
                    legal_moves.append(squares[row_index + i][square_index])
                    if square_index - 1 >= 0:
                        legal_moves.append(squares[row_index + i][square_index - 1])

                    try:
                        legal_moves.append(squares[row_index + i][square_index + 1])
                    except:
                        pass
                except:
                    pass
        self.legal_moves_improper = legal_moves

pieces = [[Pawn],[Elephant],[Horse],[Rook],[Queen],[King]]
piece_file = open('equipped_pieces.txt', 'r+')
piece1 = piece_file.readline().strip()
piece2 = piece_file.readline().strip()
piece3 = piece_file.readline().strip()
piece4 = piece_file.readline().strip()
piece5 = piece_file.readline().strip()
piece6 = piece_file.readline().strip()

def initGame(menu):
    l_king = globals()[piece6](squares[0][4], 'light')
    d_king = globals()[piece6](squares[len(squares) - 1][4], 'dark')

    l_pawn1 = globals()[piece1](squares[1][0], 'light')
    l_pawn2 = globals()[piece1](squares[1][1], 'light')
    l_pawn3 = globals()[piece1](squares[1][2], 'light')
    l_pawn4 = globals()[piece1](squares[1][3], 'light')
    l_pawn5 = globals()[piece1](squares[1][4], 'light')
    l_pawn6 = globals()[piece1](squares[1][5], 'light')
    l_pawn7 = globals()[piece1](squares[1][6], 'light')
    l_pawn8 = globals()[piece1](squares[1][7], 'light')
    l_rook1 = globals()[piece4](squares[0][0], 'light')
    l_rook2 = globals()[piece4](squares[0][7], 'light')
    l_horse1 = globals()[piece3](squares[0][1], 'light')
    l_horse2 = globals()[piece3](squares[0][6], 'light')
    l_eleph_1 = globals()[piece2](squares[0][2], 'light')
    l_eleph_2 = globals()[piece2](squares[0][5], 'light')
    l_queen = globals()[piece5](squares[0][3], 'light')

    d_pawn1 = globals()[piece1](squares[ len(squares) - 2][0], 'dark')
    d_pawn2 = globals()[piece1](squares[ len(squares) - 2][1], 'dark')
    d_pawn3 = globals()[piece1](squares[ len(squares) - 2][2], 'dark')
    d_pawn4 = globals()[piece1](squares[ len(squares) - 2][3], 'dark')
    d_pawn5 = globals()[piece1](squares[ len(squares) - 2][4], 'dark')
    d_pawn6 = globals()[piece1](squares[ len(squares) - 2][5], 'dark')
    d_pawn7 = globals()[piece1](squares[ len(squares) - 2][6], 'dark')
    d_pawn8 = globals()[piece1](squares[ len(squares) - 2][7], 'dark')
    d_rook1 = globals()[piece4](squares[len(squares) - 1][0], 'dark')
    d_rook2 = globals()[piece4](squares[len(squares) - 1][7], 'dark')
    d_horse1 = globals()[piece3](squares[len(squares) - 1][1], 'dark')
    d_horse2 = globals()[piece3](squares[len(squares) - 1][6], 'dark')
    d_eleph_1 = globals()[piece2](squares[len(squares) - 1][2], 'dark')
    d_eleph_2 = globals()[piece2](squares[len(squares) - 1][5], 'dark')
    d_queen = globals()[piece5](squares[len(squares) - 1][3], 'dark')
    menu.deleteLater()


    for key, value in ChessPieces.pieces_dict.items():
        if value == 'dark':
            key.setAttribute(Qt.WA_TransparentForMouseEvents, True)


def pieceMenu(main_window, main_menu):
    menu = QWidget(main_window)
    menu.setStyleSheet('background-color: yellow;')
    menu.setGeometry(main_menu.geometry())
    white_menu = QWidget(menu)
    white_menu_layout = QVBoxLayout(white_menu)

    def expandMenu(piece_type, menu):
        layout = QHBoxLayout(menu)
        piece_row = []
        for pieceRow in pieces:
            if piece_row != []:
                break
            for piece in pieceRow:
                if piece == piece_type:
                    piece_row = pieceRow
                    break
        for piece in piece_row:
            button = QPushButton()
            # button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setIcon(piece.icon())
            button.setIconSize(button.size() / 16)
            button.clicked.connect(lambda _, x=piece: expandMenu(type(x), menu))
            layout.addWidget(button)
    def equipPiece():
        pieces = []
        
    def generatePieceMenu(menu, color):
        banned_pieces = []
        equipped_pieces = []
        for piece in ChessPieces.pieces_dict:
            if type(piece) in banned_pieces:
                continue
            elif piece.piece_color == color:
                equipped_pieces.append(piece)
                banned_pieces.append(type(piece))
        for piece in equipped_pieces:
            button = QPushButton()
            # button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setIcon(piece.icon())
            button.setIconSize(button.size() / 16)
            button.clicked.connect(lambda _, x=piece: expandMenu(type(x), menu))
            menu.addWidget(button)

    menu.show()
    main_menu.deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_window = MainWindow()
    start_window.show()

    sys.exit(app.exec_())