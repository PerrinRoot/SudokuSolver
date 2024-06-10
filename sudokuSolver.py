import tkinter as tk
from tkinter import messagebox
import threading
import time

# Sudoku solving function with optimization and constraint propagation
def is_safe(board, row, col, num):
    for x in range(9):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def find_empty_location(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def find_empty_location_with_mrv(board):
    min_options = 10  # More than the max number of options (1-9)
    best_cell = None
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                num_options = sum(is_safe(board, i, j, num) for num in range(1, 10))
                if num_options < min_options:
                    min_options = num_options
                    best_cell = (i, j)
    return best_cell

def solve_sudoku(board, timeout=5):
    start_time = time.time()

    def solve():
        if time.time() - start_time > timeout:
            return False
        empty = find_empty_location_with_mrv(board)
        if not empty:
            return True
        row, col = empty
        for num in sorted(range(1, 10), key=lambda x: -count_conflicts(board, row, col, x)):
            if is_safe(board, row, col, num):
                board[row][col] = num
                if solve():
                    return True
                board[row][col] = 0
        return False

    result = [False]

    def thread_solve():
        result[0] = solve()

    solver_thread = threading.Thread(target=thread_solve)
    solver_thread.start()
    solver_thread.join(timeout)
    if solver_thread.is_alive():
        return False
    return result[0]

def count_conflicts(board, row, col, num):
    conflicts = 0
    for x in range(9):
        if board[row][x] == num or board[x][col] == num:
            conflicts += 1
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                conflicts += 1
    return conflicts

# GUI application
class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.solved_cells = set()
        self.current_row = 0
        self.current_col = 0
        self.create_grid()
        self.solve_button = tk.Button(self.root, text="Solve Sudoku", command=self.solve)
        self.solve_button.place(x=100, y=500)
        self.clear_button = tk.Button(self.root, text="Clear Board", command=self.clear_board)
        self.clear_button.place(x=270, y=500)

        # Bind arrow keys
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

    def create_grid(self):
        self.canvas = tk.Canvas(self.root, width=450, height=450)
        self.canvas.place(x=25, y=25)

        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            if i < 9:  # Only draw the grid lines within the 9x9 area
                self.canvas.create_line(0, i * 50, 450, i * 50, width=width)
                self.canvas.create_line(i * 50, 0, i * 50, 450, width=width)
        
        # Drawing the topmost and leftmost bold lines manually
        self.canvas.create_line(0, 0, 450, 0, width=3)
        self.canvas.create_line(0, 0, 0, 450, width=3)

        for row in range(9):
            for col in range(9):
                entry = tk.Entry(self.root, width=2, font=('Arial', 18), justify='center', relief='solid', bd=1)
                entry.place(x=col * 50 + 30, y=row * 50 + 30, width=40, height=40)
                entry.bind("<KeyRelease>", self.validate_input)
                entry.bind("<Button-1>", self.click_cell)
                self.cells[row][col] = entry

        self.highlight_current_cell()

    def validate_input(self, event):
        widget = event.widget
        value = widget.get()
        if value not in ('', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            widget.delete(0, tk.END)
            messagebox.showerror("Invalid Input", "Please enter a number between 1 and 9.")

    def click_cell(self, event):
        widget = event.widget
        for row in range(9):
            for col in range(9):
                if self.cells[row][col] == widget:
                    self.current_row, self.current_col = row, col
                    self.highlight_current_cell()
                    return

    def highlight_current_cell(self):
        for row in range(9):
            for col in range(9):
                if (row, col) in self.solved_cells:
                    self.cells[row][col].config(bg="lightyellow")
                else:
                    self.cells[row][col].config(bg="white")

        self.cells[self.current_row][self.current_col].config(bg="white")
        self.cells[self.current_row][self.current_col].focus_set()

    def move_up(self, event):
        self.current_row = (self.current_row - 1) % 9
        self.highlight_current_cell()

    def move_down(self, event):
        self.current_row = (self.current_row + 1) % 9
        self.highlight_current_cell()

    def move_left(self, event):
        self.current_col = (self.current_col - 1) % 9
        self.highlight_current_cell()

    def move_right(self, event):
        self.current_col = (self.current_col + 1) % 9
        self.highlight_current_cell()

    def get_board(self):
        board = []
        for row in range(9):
            current_row = []
            for col in range(9):
                val = self.cells[row][col].get()
                if val == '':
                    current_row.append(0)
                else:
                    current_row.append(int(val))
            board.append(current_row)
        return board

    def set_board(self, board):
        for row in range(9):
            for col in range(9):
                if board[row][col] != 0:
                    if self.cells[row][col].get() == '':
                        self.solved_cells.add((row, col))
                        self.cells[row][col].config(bg="lightyellow")
                    self.cells[row][col].delete(0, tk.END)
                    self.cells[row][col].insert(0, board[row][col])

    def solve(self):
        board = self.get_board()
        if solve_sudoku(board):
            self.set_board(board)
        else:
            messagebox.showerror("Error", "No solution exists or solving timed out!")

    def clear_board(self):
        for row in range(9):
            for col in range(9):
                self.cells[row][col].delete(0, tk.END)
                self.cells[row][col].config(bg="white")
        self.solved_cells.clear()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x600")
    app = SudokuGUI(root)
    root.mainloop()
