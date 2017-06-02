
import random
import os
from table import Table, LogEntry, RacketData, BallData, CardData, DIM, TMAX, PL, RS
import shelve,time


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
    return main_table.winner



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

def gentic_algorthim(data) :
    west_data,east_data = random.sample(data,2)
    print(west_data,'vs',east_data)
    WP.adjust_fac(west_data[0], west_data[1])
    EP.adjust_fac(east_data[0], east_data[1])
    winner = race(west_name, WP.serve, WP.play, WP.summarize, east_name, EP.serve, EP.play, EP.summarize)
    if winner == 'West' :
        data.remove(east_data)
    else:
        data.remove(west_data)

west_name,east_name = 'T_fac_compare','T_fac_compare_beta'
exec('import %s as WP' % (west_name,))
exec('import %s as EP' % (east_name,))

dataNum = int(input())
data = generate_factors(dataNum)
while len(data) > 1 :
    print(len(data))
    gentic_algorthim(data)
f_last = open('./f_last.txt','a')
retData = "%s'\n'%s'\n'"%(dataNum,data)
f_last.write(retData)
f_last.close()
print(data)

