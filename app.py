from flask import Flask, render_template, request
from sudoku import randomizeSudoku, generateSudoku, SUDOKU_SIZE
from multiprocessing import Process, Queue

app = Flask(__name__)

BUF_SIZE = 10
sudokuQueue = Queue(BUF_SIZE)
formValues = [[]]

def construct_answer_key(sudoku_answer, sudoku_grid):
    answer_key =  dict()
    for row in range(SUDOKU_SIZE):
        for column in range(SUDOKU_SIZE):
            if sudoku_grid[row][column] == 0:
                answer_key["{}{}".format(row, column)] = str(sudoku_answer[row][column])
    return answer_key


def construct_sudokus(sudokus):
    while True:
        if not sudokus.full():
            s = randomizeSudoku()
            s_grid = generateSudoku(s)
            s_answer = construct_answer_key(s, s_grid)
            print("Added 1 new sudoku")
            sudokus.put((s, s_grid, s_answer))

# First time starting the app
sudoku = randomizeSudoku()
sudoku_grid = generateSudoku(sudoku)
answer_key = construct_answer_key(sudoku, sudoku_grid)

@app.route('/', methods=['POST', 'GET'])
def home():
    global sudoku_grid, sudoku, sudokuQueue

    if request.method == 'POST':
        result = request.form.to_dict()  # sudoku form
        answer_key = construct_answer_key(sudoku, sudoku_grid)
        print("result: ", result)
        print("answer", answer_key)

        if result == answer_key: # user solved the sudoku
            return render_template('Home.html', message="Good job!", sudoku=sudoku_grid, enumerate=enumerate, str=str, formValues=result, canChange=True)
        else:
            difference = sorted([pos for pos in answer_key if result[pos] != answer_key[pos]])
            print(difference)
            return render_template('Home.html', message="It's not good :( Try again!", sudoku=sudoku_grid, difference=difference, enumerate=enumerate, str=str, formValues=result)

    else: # GET method
        return render_template('Home.html', sudoku=sudoku_grid, enumerate=enumerate, str=str)


@app.route('/newsudoku', methods=['GET'])
def changeSudoku():
    global sudoku, answer_key, sudoku_grid
    # Give a new sudoku
    (v1, v2, v3) = sudokuQueue.get()
    sudoku = v1
    sudoku_grid = v2
    answer_key = v3
    return render_template('Home.html', sudoku=sudoku_grid, enumerate=enumerate, str=str)


if __name__ == '__main__':
    p = Process(target=construct_sudokus, args=(sudokuQueue,))
    p.start()
    app.run(threaded=True, debug=True)
    p.join()

