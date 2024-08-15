To do:
 - split Board into Board, GameInfo, Controller, Monitor
    - Board: accessing current gamestate
    - GameInfo: accessing metadata, beyond typical gamestate info, importing/exporting
    - Controller: movement operations and changing gamestate
    - Evaluator: evaluating gamestate, determining end conditions and valid moves
       - Knight(Evaluator)
       - Bishop(Evaluator)
       - King(Evaluator)
       - ...
 - Implement threefold repetition - counter of fen states that
     gets reset upon capture/pawn move
 - cleanse move() of preemptive conditional logic
 - use inherited self.out_of_bounds() instead of invoking super()
 - Rip board out of pieces
    - pieces should not be able to see pieces on other squares
    - should just be: does piece follow conventional movement?
    - Controller/Evaluator determines valid moves
        
