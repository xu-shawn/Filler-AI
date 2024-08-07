from board import Board
from anytree import Node as AnyNode
import cProfile


class MinMax:
    INFINITY = 100000

    def __init__(self, gameBoard : Board) -> None:
        self.gameBoard : Board = gameBoard

    def getAvailableMoves(self, color1 : int, color2 : int) -> list[int]:
        moves = [0, 1, 2, 3, 4, 5]
        moves.remove(color1)
        # Sometimes the board generates with both players starting the same color
        try:
            moves.remove(color2)
        except:
            pass
        return moves

    # Checks each neighbor of the player starting from the corner, if same color then it gets added to the list
    def findPlayerPositions(self, board : list[list]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        player1: tuple[int, int] = (0, 7)
        player2: tuple[int, int] = (6, 0)

        def helper(playerPosition : tuple[int, int]) -> list[tuple[int, int]]:
            toCheck: set[tuple[int, int]] = {playerPosition}
            new_positions: set[tuple[int, int]] = {playerPosition}
            visited: set[tuple[int, int]] = set()

            neighbors: set[tuple[int, int]] = {
                (-1, 0), (1, 0), (0, -1), (0, 1)
            }

            while new_positions:
                next_positions: set[tuple[int, int]] = set()
                for pos in new_positions:
                    for dx, dy in neighbors:
                        neighbor = (pos[0] + dx, pos[1] + dy)
                        if neighbor not in visited and 0 <= neighbor[0] < len(board) and 0 <= neighbor[1] < len(board[0]):
                            if board[neighbor[0]][neighbor[1]] == board[pos[0]][pos[1]]:
                                next_positions.add(neighbor)
                                visited.add(neighbor)
                toCheck.update(next_positions)
                new_positions = next_positions

            return list(toCheck)

        return helper(player1), helper(player2)

    # This will convery all player positions to the color selected
    def simulate(self, colors : list[int], origBoard : Board) -> int:
        board = origBoard.getBoardCopy()
        perspective = True
        for color in colors[2:]:
            positions = self.findPlayerPositions(board)
            if perspective:
                perspective = False
                for pos in positions[0]:
                    board[pos[0]][pos[1]] = color
            else:
                perspective = True
                for pos in positions[1]:
                    board[pos[0]][pos[1]] = color

        # If position is winning give it a greater value (Or lesser if its the opponent)
        positions: tuple[list[tuple[int, int]], list[tuple[int, int]]] = self.findPlayerPositions(board)
        if len(positions[0]) > 28:
            return 100 + len(positions[0])
        elif len(positions[1]) > 28:
            return -100 - len(positions[1])

        return len(positions[0]) - len(positions[1])

    def generateTree(self, node: AnyNode, maxDepth : int, depth : int, a: int, b: int, maximizing_player: bool) -> tuple[AnyNode | None, int, list[list[int]] | None]:
        if depth == maxDepth:
            return None, self.simulate(node.colors, self.gameBoard), [node.colors]

        best_child = None
        best_eval: int = -self.INFINITY if maximizing_player else self.INFINITY
        best_path_colors: list[list[int]] | None = None

        # Branch off for each of the four moves
        for move in self.getAvailableMoves(node.colors[-2], node.colors[-1]):
            newColors = node.colors.copy()
            newColors.append(move)
            child_node: AnyNode = AnyNode(name=f"{node.name}{move}", parent=node, colors=newColors)

            # Evaluate the child node using Minimax
            _, eval, path = self.generateTree(child_node, maxDepth, depth + 1, a, b, not maximizing_player)

            if maximizing_player:
                if eval > best_eval:
                    best_eval = eval
                    best_child = child_node
                    best_path_colors = path + [child_node.colors]
                    a = max(a, eval)
                    if(a >= b):
                        break
            else:
                if eval < best_eval:
                    best_eval = eval
                    best_child = child_node
                    best_path_colors = path + [child_node.colors]
                    b = min(b, eval)
                    if(b >= a):
                        break

            #in theory this should be faster but its not for some reason?????? i have no clue why
            #if b <= a:
            #    print("branch pruned! maxxingplayer: " + str(maximizing_player))
            #    print("depth: " + str(depth))
            #    break  # Alpha-beta pruning

        return best_child, best_eval, best_path_colors

    def evaluate_tree(self, board : Board, maxDepth : int, isPlayer1) -> tuple[list[list[int]], int]:
        root: AnyNode = AnyNode(name="Root", colors=[board.board[6][0], board.board[0][7]])
        _, best_score, best_path_colors = self.generateTree(root, maxDepth, 0, -self.INFINITY, self.INFINITY, isPlayer1)
        assert best_path_colors is not None
        return best_path_colors, best_score


# def main():
#     test = Board(8)
#     test.buildBoard()
#     testClass = MinMax(test)

#     print("Creating and Evaluating Tree")

#     # Evaluate the tree using Minimax to find the best score
#     best_path_colors, best_score = testClass.evaluate_tree(test, 12)
#     print(f"Best moves found using Minimax were: {best_path_colors[0][2:]} with score of: {best_score}")

#     test.printBoard()

# cProfile.run("main()")
