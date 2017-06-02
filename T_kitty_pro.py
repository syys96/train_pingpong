from table import *

APP_PRRORITY = [CARD_SPIN, CARD_INCL, CARD_AMPL, CARD_DECL, CARD_TLPT, CARD_DSPR]
PICK_PRIORITY = [CARD_INCL, CARD_SPIN, CARD_AMPL, CARD_DECL, CARD_TLPT, CARD_DSPR]#实际顺序不一定如此

"""
self_pos_factors = [0.48, 0.115, 0.405]
enemy_pos_factors = [0.42021276595744683, 0.4734042553191489, 0.10638297872340426]
eva_factors = (1, 1, -1)

"""
self_pos_factors = [0.725, 0.125, 0.15]
enemy_pos_factors = [0.6447368421052632, 0.046052631578947366, 0.3092105263157895]
eva_factors = (1, 1, -1)


"""
(1).优化了避免'invalid bounce'的代码,改进了跑位算法和估值函数中对方对我方推测的设定；
(2).对于不同对手的算法，最佳参数的设置也有很大差别；所以参数的设置只能针对普遍、平均情况，追求平均胜率而不是优势差距的大小
(3).对游戏结果的制约有如下因素:
    1.随机性，包括道具的种类、数量和出现位置;
    2.跑位的不确定性，不同算法对此的认识和解决方法不同;
    3.不同的算法中，捡道具、打角和道具使用、对特殊道具的防范均不同;
(4).
    待调整参数:TOOL_VALUE,eva_factors,self_pos_factors,enemy_pos_factors
"""
"""
描述道具价值的字典，参数可调
"""
CARD_AMPL_VALUE = 600
CARD_TLPT_VALUE = 500
CARD_DSPR_VALUE = 100
CARD_SPIN_VALUE = 500
TOOL_VALUE = {CARD_INCL: CARD_INCL_PARAM,
              CARD_DECL: CARD_DECL_PARAM,
              CARD_AMPL: CARD_AMPL_VALUE,
              CARD_TLPT: CARD_TLPT_VALUE,
              CARD_DSPR: CARD_DSPR_VALUE,
              CARD_SPIN: CARD_SPIN_VALUE,
              'NOCARD': 0}


# 发球不消耗生命值，因此选择打角
def serve( op_side,ds: dict) -> tuple:
    tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
    Vy = 3 * (DIM[3] - DIM[2]) // tick_step // 2
    return ((DIM[2] + DIM[3]) // 2, Vy)


def play(tb: TableData, ds: dict) -> RacketAction:
    retCard = getCard(tb, ds)
    ball_Vy = tb.ball['velocity'].y
    ball_posX,ball_posY = tb.ball['position'].x,tb.ball['position'].y
    tools = tb.cards['cards']
    op_side_X = tb.op_side['position'].x
    op_side_Y = tb.op_side['position'].y
    op_active_card = tb.op_side['active_card'][1]
    ENEMY_POSITION_Y = get_opside_pos(ball_Vy,ball_posX,ball_posY,op_side_Y)
    retAcc = getAcc(ball_Vy,ball_posX,ball_posY,tools,ENEMY_POSITION_Y,op_active_card)
    posVector = positioning(tb, ds)
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, retAcc, posVector, retCard[0],retCard[1])


def getCard(tb: TableData, ds: dict) -> tuple:
    for card in APP_PRRORITY:
        if card in tb.side['cards']:
            if card == CARD_INCL and tb.side['life'] < RACKET_LIFE - CARD_INCL_PARAM:
                return tb.side, card
            elif card == CARD_DECL or card == CARD_AMPL or card == CARD_SPIN:
                return tb.op_side, card
            elif card == CARD_TLPT or card == CARD_DSPR:
                return tb.side, card
    return None, None


def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return


def getAcc(ball_Vy:int, ball_posX:int,ball_posY:int,tools:Card,enemy_posY,op_active_card=None) -> int:
    tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
    Pos_Y = ball_posY
    Vy = ball_Vy
    upMin = int((DIM[3] - Pos_Y) // tick_step - Vy)
    upMax = int((2 * (DIM[3] - DIM[2]) + DIM[3] - Pos_Y) // tick_step - Vy)
    downMax = int((-1) * (Pos_Y - DIM[2]) // tick_step - Vy)
    downMin = int((-1) * (2 * (DIM[3] - DIM[2]) + Pos_Y - DIM[2]) // tick_step - Vy)

    newUpmin, newUPmax, newDownmin, newDownmax = upMin + 1, upMax - 1, downMin + 1, downMax - 1
    if op_active_card == CARD_SPIN:  # 如果对方使用旋转球, 则调整合法加速值范围
        if (upMin + 1) < 0 and (upMax - 1) < 0:
            newUpmin, newUPmax = upMin + 1, (upMax - 1) * 2
        elif (upMin + 1) > 0 and (upMax - 1) > 0:
            newUpmin, newUPmax = (upMin + 1) * 2, upMax - 1
        if (downMin + 1) < 0 and (downMax - 1) < 0:
            newDownmin, newDownmax = downMin + 1, (downMax - 1) * 2
        elif (downMin + 1) > 0 and (downMax - 1) > 0:
            newDownmin, newDownmax = (downMin + 1) * 2, downMax - 1

    # 捡道具
    cards_deltaV = hitCards_delta_Vy(ball_Vy,ball_posX,ball_posY,tools)
    MINVALUE = -100000
    FINALCHOICE = None
    for var in cards_deltaV:
        if int(var[1]) in range(newUpmin, newUPmax) or int(var[1]) in range(newDownmin, newDownmax):
            value = evalueate(ball_Vy, ball_posY, var[0], var[1],enemy_posY)
            if value > MINVALUE:
                MINVALUE = value
                FINALCHOICE = var

    # 不捡道具
    MAX_VALUE = -90000
    for dt in range(newUpmin, newUPmax, 10):
        value = evalueate(ball_Vy, ball_posY, 'NOCARD', dt,enemy_posY)
        if value > MAX_VALUE:
            MAX_VALUE = value
            retV = dt
    for dt in range(newDownmin, newDownmax, 10):
        value = evalueate(ball_Vy, ball_posY, 'NOCARD', dt,enemy_posY)
        if value > MAX_VALUE:
            MAX_VALUE = value
            retV = dt
    # 综合考虑选择估值较大的加速值
    if MINVALUE > MAX_VALUE:
        return int(FINALCHOICE[1])
    else:
        return retV

#计算能够捡到的道具和对应的加速值
def hitCards_delta_Vy(ball_Vy:int, ball_posX:int,ball_posY:int, tools:Card) -> list:  # list of (card,deltaV)
    retVys = []
    cards = [card.code for card in tools]  # cards is list of string
    for card in PICK_PRIORITY:
        if card in cards:
            for var in tools:
                if var.code == card:
                    pos = var.pos  # Vector
                    step = abs(pos.x - ball_posX) / BALL_V[0]
                    retVys.append((card, (pos.y - ball_posY) / step - ball_Vy))
                    retVys.append((card, (DIM[3] - ball_posY + DIM[3] - pos.y) / step - ball_Vy))
                    retVys.append((card,(DIM[3] - ball_posY + DIM[3] - DIM[2] + pos.y - DIM[2]) / step - ball_Vy))
                    retVys.append((card, (-1) * (ball_posY - DIM[2] + pos.y - DIM[2]) / step - ball_Vy))
                    retVys.append((card,(-1) * (ball_posY - DIM[2] + DIM[3] - DIM[2] + DIM[3] - pos.y) / step -ball_Vy))
    return retVys


"""
跑位:
(1):不跑;
(2):跑到中间;
(3):推测对方会选择对我方最不利的加速值(未考虑对方捡道具)，以此计算对方打回的球的位置，作为我方跑位的目标;
(4):综合以上三种因素加权得出最后结果，并选择跑一半(与迎球配合)
(5):缺陷:未考虑捡道具的情况,然而道具是随机出现的;
"""
def positioning(tb: TableData, ds: dict) -> int:
    if tb.side['life'] > 55000:
        if tb.ball['position'].y < ((DIM[3]-DIM[2])//3):
            return (DIM[3]-DIM[2])/3-tb.ball['position'].y
        elif tb.ball['position'].y > ((DIM[3]-DIM[2])*2//3) :
            return (DIM[3]-DIM[2])*2/3-tb.ball['position'].y
        else:
            return 0
    else:
        return int((DIM[3] - DIM[2]) // 2 - tb.ball['position'].y)


def get_opp_posY(ball_Vy:int, ball_posY:int,deltaVy:int) -> int :
    tick_step = (DIM[1] - DIM[0]) / BALL_V[0]
    distance = abs(ball_Vy + deltaVy) * tick_step
    if ball_Vy + deltaVy > 0 :
        if ((distance - (DIM[3] - ball_posY)) // (DIM[3] - DIM[2])) % 2 == 0:
            opponentY = DIM[3] - ((distance - (DIM[3] - ball_posY)) % (DIM[3] - DIM[2]))
        else:
            opponentY = ((distance - (DIM[3] - ball_posY)) % (DIM[3] - DIM[2]))
    else:
        if ((distance - ball_posY) // (DIM[3] - DIM[2])) % 2 == 0:
            opponentY = (distance - ball_posY) % (DIM[3] - DIM[2])
        else:
            opponentY = DIM[3] - (((distance - ball_posY) % (DIM[3] - DIM[2])))
    return opponentY

"""
估值函数:
value(action) = factor(1)*value(card) + factor(2)*loss(opponent)+factor(3)*loss(self)
factor(i)为可调参数，原始值为1，1，-1
该函数描述了对我方有利的程度，估值越大对我方越有利
"""
def evalueate(ball_Vy:int, ball_posY:int, card, deltaV,enemy_posY) -> int:
    toolEffect = TOOL_VALUE[card]
    selfLoss = (abs(deltaV) ** 2) / (FACTOR_SPEED ** 2)
    opponentY = get_opp_posY(ball_Vy,ball_posY,deltaV)
    enemyLoss = (abs(enemy_posY - opponentY) ** 2) / (FACTOR_DISTANCE ** 2)
    return int(eva_factors[0] * toolEffect + eva_factors[1] * enemyLoss + eva_factors[2] * selfLoss)

#不考虑捡道具我方应该做出的选择，即对方对我的推测;最后返回我对对方跑位位置的预测
def get_opside_pos(ball_Vy,ball_posX,ball_posY,opside_posY:int) :
    pos0 = opside_posY #不跑,这是intelligent的做法，然而在参数设置[0.2,0.3,0.5]中只占了0.2,所以估计不准，优势不大
    pos1 = (DIM[3] - DIM[2]) // 2
    #此处默认为"他认为我认为他跑位原地不动":enemy_posY = opside_posY
    notools_Acc = getAcc(ball_Vy,ball_posX,ball_posY,[],opside_posY)
    pos2 = get_opp_posY(ball_Vy,ball_posY,notools_Acc)
    pos = pos0*enemy_pos_factors[0] + pos1*enemy_pos_factors[1] + pos2*enemy_pos_factors[2]
    return pos
