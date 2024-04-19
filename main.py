from wtforms import StringField, SubmitField, BooleanField
from flask_wtf import FlaskForm
from flask import Flask, render_template, request
import enum
import copy

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'SIH*v-6u)c>q<;;h&);cRw,1E_CO8>'

class GameForm(FlaskForm):
  choice = StringField("Choose number: ")
  renew = BooleanField("Do you want to restart game?")
  button = SubmitField("Make Turn")


class Player:
  def __init__(self, name, victories, symbol):
      self.name = name
      self.victories = victories
      self.symbol = symbol

  def increase_victoies(self):
      self.victories += 1

  def null_victories(self):
      self.victories = 0

  def check_win_conditions(self, made_turns):
      win_condition = [self.symbol, self.symbol, self.symbol]
      possible_combinations = (made_turns[0:3], made_turns[3:6], made_turns[6:9],
                               made_turns[1:9:3], made_turns[2:11:3], made_turns[0:9:4],
                               made_turns[2:8:2], made_turns[0:8:3])
      if win_condition in possible_combinations:
          return True
      else:
          return False


class ErrorMessage(enum.Enum):
  out_of_range = "Input should be integer in range (0,8)"
  choice_earlier = "The position was chosen earlier"


class GameLogic:
  def choose_active_player(first_hand, turn, player1, player2):
      if first_hand and turn == 0:
          active_player = copy.deepcopy(player1)
      elif first_hand and turn == 1:
          active_player = copy.deepcopy(player2)
      elif not first_hand and turn == 0:
          active_player = copy.deepcopy(player2)
      else:
          active_player = copy.deepcopy(player1)
      return active_player

  def renew_button_submit(_renew, _positions, _turn, _win_condition, _draw, _error,
                          _player1_victories, _player2_victories, _round_number, _step):
      _renew = True
      _positions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
      _turn = 0
      _win_condition = False
      _draw = False
      _error = ""
      _player1_victories = 0
      _player2_victories = 0
      _round_number = 1
      _step = 0

      return (_renew, _positions, _turn, _win_condition, _draw, _error,
                          _player1_victories, _player2_victories, _round_number, _step)


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
positions = [0, 1, 2, 3, 4, 5, 6, 7, 8] # this is possible positions to put X or O
turn = 0  # shows what player make step at the moment, connected with round number
round_number = 1
step = 0  # number of step in current round, max value is 9 not 8
player1_victories = 0
player2_victories = 0
win_condition = False  # check if there is victory condition in the round
renew = False  # allows to reset play data
draw = False  # check if it was draw in the current round


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/game_page', methods=["GET", "POST"])
def game():
  global step
  global win_condition
  global positions
  global turn
  global renew
  global player1_victories
  global player2_victories
  global round_number
  global draw
  form = GameForm()
  error = ""
  winner = ""
  first_hand = (round_number % 2 == 1)
  if first_hand:
      player1 = Player(request.args.get('first_player_name'), player1_victories, "X")
      player2 = Player(request.args.get('second_player_name'), player2_victories, "O")
  else:
      player1 = Player(request.args.get('first_player_name'), player1_victories, "O")
      player2 = Player(request.args.get('second_player_name'), player2_victories, "X")

  active_player = GameLogic.choose_active_player(first_hand, turn, player1, player2)

  if form.validate_on_submit():
      if form.renew.data:
          # renew all
          (renew, positions, turn, win_condition,
           draw, error, player1_victories,
           player2_victories, round_number, step) = GameLogic.renew_button_submit(renew, positions, turn,
                                                                                  win_condition, draw, error,
                                                                                  player1_victories,
                                                                                  player2_victories, round_number,
                                                                                  step)
          form.renew.data = False
          player1.null_victories()
          player2.null_victories()
          player1 = Player(request.args.get('first_player_name'), player1_victories, "X")
          player2 = Player(request.args.get('second_player_name'), player2_victories, "O")
          active_player = copy.deepcopy(player1)
      else:
          renew = False
          turn_choice = form.choice.data
          try:
              turn_choice = int(turn_choice)
          except ValueError:
              error = ErrorMessage.out_of_range.value
          else:
              if turn_choice > 8:
                  error = ErrorMessage.out_of_range.value
              else:
                  if positions[turn_choice] in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                      step += 1
                      positions[turn_choice] = active_player.symbol
                      win_condition = active_player.check_win_conditions(positions)
                      draw = step == 9
                      error = ""
                      if win_condition:
                          step = 0
                          round_number += 1
                          turn = 0
                          positions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                          if active_player.name == player1.name:
                              player1_victories += 1
                              player1.increase_victoies()
                              winner = player1
                              del active_player
                              if round_number % 2 == 1:
                                  active_player = Player(request.args.get('first_player_name'),
                                                         player1_victories, "X")
                              else:
                                  active_player = Player(request.args.get('second_player_name'),
                                                         player2_victories, "X")
                          else:
                              player2_victories += 1
                              player2.increase_victoies()
                              winner = player2
                              del active_player
                              if round_number % 2 == 1:
                                  active_player = Player(request.args.get('first_player_name'),
                                                         player1_victories, "X")
                              else:
                                  active_player = Player(request.args.get('second_player_name'),
                                                         player2_victories, "X")
                      elif draw:
                          round_number += 1
                          turn = 0
                          positions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                          step = 0
                          winner = None
                          del active_player
                          if round_number % 2 == 1:
                              active_player = Player(request.args.get('first_player_name'),
                                                     player1_victories, "X")
                          else:
                              active_player = Player(request.args.get('second_player_name'),
                                                     player2_victories, "X")
                      else:
                          turn = 1 - turn  # if was 0 we get 1, if it was 1 we get 0
                          active_player = GameLogic.choose_active_player(first_hand, turn, player1, player2)
                  else:
                      error = ErrorMessage.choice_earlier.value

  form.choice.data = ""
  return render_template('game_page.html', form=form, error=error, positions=positions,
                         win_condition=win_condition, renew=renew, player1=player1, player2=player2,
                         active_player=active_player, winner=winner, draw=draw)


if __name__ == '__main__':
  app.run(debug=False)