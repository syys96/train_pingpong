import random
import os
import show
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
    if main_table.winner == 'West' :
        f_name = "./f_data_%s.txt"%(east_name,)
        f_data = open(f_name, 'a')
        global data
        log = "%s'\n'%s'\n'" % ((main_table.players['West'].life, main_table.players['East'].life), data)
        f_data.write(log)
        f_data.close()

    #time.sleep(5)
    #show.main(log,main_table.winner,main_table.reason)
    #testcode.main(log,main_table.winner,main_table.reason)


def generate_factors(number) :
    retFacs = []
    for i in range(number) :
        a, b, c,d = random.randint(0, 100), random.randint(0, 100), random.randint(0, 100),random.randint(0,100)
        a, b, c,d = a / (a + b + c+d), b / (a + b + c+d), c / (a + b + c+d),d/(a+b+c+d)
        self = [a, b, c,d]
        a, b, c = random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)
        a, b, c = a / (a + b + c), b / (a + b + c), c / (a + b + c)
        ennmy = [a, b, c]
        retFacs.append((self,ennmy))
    return retFacs

players = [f[:-3] for f in os.listdir('.') if os.path.isfile(f) and f[-3:] == '.py' and f[:2] == 'T_']
for i in range(len(players)) :
    print(i,' ',players[i])
print('选择测试对手:(请输入序号,从0开始)')
east_name = players[int(input())]
west_name = 'T_fac_compare'
exec('import %s as WP' % (west_name,))
exec('import %s as EP' % (east_name,))

fac_data = generate_factors(20)
for data in fac_data :
    WP.adjust_fac(data[0],data[1])
    race(west_name, WP.serve, WP.play, WP.summarize, east_name, EP.serve, EP.play, EP.summarize)

