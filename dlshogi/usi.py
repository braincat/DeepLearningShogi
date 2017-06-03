from dlshogi.policy_network import *
from dlshogi.common import *

import cppshogi

from chainer import serializers

def main():
    # default option value
    modelfile = r'H:\src\DeepLearningShogi\dlshogi\model_sl_elmo1000-009'
    evaldir = r'H:\src\elmo_for_learn\bin\20161007'

    while True:
        cmd_line = input()
        cmd = cmd_line.split(' ', 1)
        print('info string', cmd)

        if cmd[0] == 'usi':
            print('id name dlshogi')
            print('id author Tadao Yamaoka')
            print('option name modelfile type filename default', modelfile)
            print('option name evaldir type string default', evaldir)
            print('usiok')
        elif cmd[0] == 'setoption':
            opt = cmd[1].split(' ')
            if opt[1] == 'modelfile':
                modelfile = opt[3]
                print('info string', modelfile)
            elif opt[1] == 'evaldir':
                evaldir = opt[3]
                print('info string', evaldir)
        elif cmd[0] == 'isready':
            # init cppshogi
            cppshogi.setup_eval_dir(evaldir)
            engine = cppshogi.Engine()

            model = PolicyNetwork()
            model.to_gpu()
            serializers.load_npz(modelfile, model)
            print('readyok')
        elif cmd[0] == 'usinewgame':
            continue
        elif cmd[0] == 'position':
            # cppshogi
            engine.position(cmd[1])
        elif cmd[0] == 'go':
            # cppshogi
            usi_move, usi_score = engine.go()
            #print(usi_move, usi_score)

            features1 = np.empty((1, 2 * 14, 9, 9), dtype=np.float32)
            features2 = np.empty((1, 2 * MAX_PIECES_IN_HAND_SUM + 1, 9, 9), dtype=np.float32)
            turn = engine.make_input_features(features1, features2)

            x1 = Variable(cuda.to_gpu(features1))
            x2 = Variable(cuda.to_gpu(features2))

            y = model(x1, x2, test=True)

            y_data = cuda.to_cpu(y.data)

            move = engine.select_move(y_data)
            
            # check score
            if usi_score >= 3000:
                print('bestmove', usi_move)
                continue
            elif usi_score < -3000:
                print('bestmove resign')
                continue

            print('bestmove', move)
        elif cmd[0] == 'quit':
            break

if __name__ == '__main__':
    main()