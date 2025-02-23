from piece_info import board_to_coord

class Handler:
    def get_move(self) -> str:
        move = input("Enter a move:")
        res = self.parse_move(move)
        while not res["valid"]:
            print(res["reason"])
            move = input("Enter a move:")
            res = self.parse_move(move)
        return res

    def parse_move(self, move: str) -> dict[str, any]:
        res = {"valid": False, "reason": ""}
        move = move.lower()

        if len(move) < 4:
            res["reason"] = f"Error: Invalid move {move}. Too short. Move must be in the format 'e2e4'."
            return res
        if move[0] not in "abcdefgh" or move[1] not in "12345678" or move[2] not in "abcdefgh" or move[3] not in "12345678":
            res["reason"] = f"Error: Invalid move {move}. Move must be in the format 'e2e4'."
            return res
        if len(move) != 4:
            if len(move) != 6:
                res["reason"] = f"Error: Invalid move {move}. Promotions must be in the format 'e7e8=q'."
                return res
            if move[4] != "=" or move[5] not in "qrbn":
                res["reason"] = f"Error: Invalid move {move}.  Promotion must be one of 'q', 'r', 'b', 'n'."
        
        res["valid"] = True
        res["start_pos"] = board_to_coord(move[0:2])
        res["end_pos"] = board_to_coord(move[2:4])
        if len(move) == 6:
            res["end_pos"] += (move[5],)
        return res

if __name__ == "__main__":
    op = Handler()
    print("Valid move:", op.parse_move("e2e4"))
    print("Valid move:", op.parse_move("e7e8=q"))
    print("Invalid move:", op.parse_move("e7e8=qw"))
    print("Invalid move:", op.parse_move("e7e8=w"))
    print("Invalid move:", op.parse_move("ee8"))
    print("Valid move:", op.parse_move("e7e8"))




    