from table import Table, LogEntry, RacketData, BallData, CardData, DIM, TMAX, PL, RS
import shelve,time,testcode


def race(west_name, west_serve, west_play, west_summarize,
         east_name, east_serve, east_play, east_summarize):
    # 生成球桌
    main_table = Table()
    main_table.players['West'].bind_play(west_name, west_serve, west_play, west_summarize)
    main_table.players['East'].bind_play(east_name, east_serve, east_play, east_summarize)
    log = list()

    # 读取历史数据，文件名为"DS-<name>"
    for side in ('West', 'East'):
        d = shelve.open('DS-%s' % (main_table.players[side].name,))
        try:
            ds = d['datastore']
        except KeyError:  # 如果这个文件没有内容，说明球队尚未建立历史数据
            ds = dict()
        finally:
            d.close()
        main_table.players[side].set_datastore(ds)

    # 发球
    main_table.serve()

    # 开始打球
    while not main_table.finished:
        # 记录日志项
        log.append(LogEntry(main_table.tick,
                            RacketData(main_table.players[main_table.side]),
                            RacketData(main_table.players[main_table.op_side]),
                            BallData(main_table.ball),
                            CardData(main_table.card_tick, main_table.cards, main_table.active_card)))
        # 运行一趟
        main_table.time_run()

    # 记录最后的回合
    log.append(LogEntry(main_table.tick,
                        RacketData(main_table.players[main_table.side]),
                        RacketData(main_table.players[main_table.op_side]),
                        BallData(main_table.ball),
                        CardData(main_table.card_tick, main_table.cards, main_table.active_card)))

    # 终局，让双方进行本局总结
    main_table.postcare()

    print("%s win! for %s, West:%s(%d）, East:%s(%d),总时间: %d tick" %
          (main_table.winner, main_table.reason,
           west_name, main_table.players['West'].life,
           east_name, main_table.players['East'].life, main_table.tick))
    global w_win,e_win
    if main_table.winner == 'West' :
        w_win += 1
    else:
        e_win += 1
    global gameNum

    if gameNum == 1 :
        print('show it ? (y/n)')
        order = input()
        if order == 'y' :
            testcode.main(log, main_table.winner, main_table.reason)
            return
    else:
        return
    #show.main(log,main_table.winner,main_table.reason)
    #testcode.main(log,main_table.winner,main_table.reason)

import os
import show
# 取得所有以T_开始文件名的算法文件名
players = [f[:-3] for f in os.listdir('.') if os.path.isfile(f) and f[-3:] == '.py' and f[:2] == 'T_']
for i in range(len(players)) :
    print(i,' ',players[i])
print('选择比赛双方:(请输入序号,从0开始,以空格隔开)')
west_index,east_index = input().split()
west_name,east_name = players[int(west_index)],players[int(east_index)]
exec('import %s as WP' % (west_name,))
exec('import %s as EP' % (east_name,))

print('please input game times :')
gameNum = int(input())

w_win,e_win = 0,0
for i in range(gameNum) :
    race(west_name, WP.serve, WP.play, WP.summarize, east_name, EP.serve, EP.play, EP.summarize)

print(w_win,e_win)
