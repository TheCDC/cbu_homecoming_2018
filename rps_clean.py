import evilrps as rps

human_player = rps.Player('Human', rps.user_move)
ai_player = rps.Player('PC', rps.create_ai())

g = rps.Game(human_player, ai_player)
while True:
    winner = g.advance()
    if winner[0] is not None:
        print(f'The winner is {winner[0].name}, who threw {winner[1].name}')
    else:
        print('Draw!')
    print('Scores:',
          ','.join(f'{p.name}: {s}' for p, s in zip(g.players, g.scores)))
