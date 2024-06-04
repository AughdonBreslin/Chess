To do:
 - Implement threefold repitition


Potentials:
 - split Board into Board and Controller or something
 - untangle board.board from pieces.py

Design choices:
 - ALL logic put into get_valid_moves()
 - is_valid_move() becomes if move in get_valid_moves()
 - PROBLEM: circular dependency between get_valid_moves(), is_valid_move(), and check().
    - get_valid_moves() requires the move doesn't open a check, check() requires that the attack on the king is a valid move, is_valid_move() requires move is among all valid moves
    - attacking piece doesnt need the attack to be valid in order for it to be a check. i.e. attacker can be pinned and still give a check
    - RESOLUTION: is_valid_move() is strictly a legal check for validity. get_valid_moves() accounts for check.
       - if is_valid_move() accounts for check, check from a pinned piece wouldn't be properly recognized.
       - removed checks for pins from is_valid_move(), gotta test

            
        
