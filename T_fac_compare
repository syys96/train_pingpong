from table import *

APP_PRRORITY = [CARD_SPIN, CARD_INCL, CARD_AMPL, CARD_DECL, CARD_TLPT, CARD_DSPR]
PICK_PRIORITY = [CARD_INCL, CARD_SPIN, CARD_AMPL, CARD_DECL, CARD_TLPT, CARD_DSPR]#实际顺序不一定如此

"""
self_pos_factors = [0.48, 0.115, 0.405]
enemy_pos_factors = [0.42021276595744683, 0.4734042553191489, 0.10638297872340426]
eva_factors = (1, 1, -1)
life_factor = 0.55

"""

#self_pos_factors = [0.4251497005988024, 0.03592814371257485, 0.12574850299401197, 0.41317365269461076]
#enemy_pos_factors = [0.4152046783625731, 0.07602339181286549, 0.5087719298245614]
#self_pos_factors = [0.391304347826087, 0.33201581027667987, 0.2608695652173913, 0.015810276679841896]
#enemy_pos_factors = [0.3346456692913386, 0.3779527559055118, 0.2874015748031496]
self_pos_factors = [0.2727272727272727, 0.3201581027667984, 0.35968379446640314, 0.04743083003952569]
enemy_pos_factors = [0.6791044776119403, 0.27611940298507465, 0.04477611940298507]
eva_factors = (1, 1, -1)
life_factor = 0.55

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
CARD_DSPR_VALUE = 300
CARD_SPIN_VALUE = 600
TOOL_VALUE = {CARD_INCL: CARD_INCL_PARAM,
              CARD_DECL: CARD_DECL_PARAM,
              CARD_AMPL: CARD_AMPL_VALUE,
              CARD_TLPT: CARD_TLPT_VALUE,
              CARD_DSPR: CARD_DSPR_VALUE,
              CARD_SPIN: CARD_SPIN_VALUE,
              'NOCARD': 0}


# 发球不消耗生命值，因此选择打角
def serve(tb: TableData, ds: dict) -> tuple:
    tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
    Vy = 3 * (DIM[3] - DIM[2]) // tick_step // 2
    return ((DIM[2] + DIM[3]) // 2, Vy)


def play(tb: TableData, ds: dict) -> RacketAction:
    ball_Vy = tb.ball['velocity'].y
    ball_posX,ball_posY = tb.ball['position'].x,tb.ball['position'].y
    tools = tb.cards['cards']
    op_side_X = tb.op_side['position'].x
    op_side_Y = tb.op_side['position'].y
    op_active_card = tb.op_side['active_card'][1]
    ENEMY_POSITION_Y = get_opside_pos(ball_Vy,ball_posX,ball_posY,op_side_Y)
    retAcc = getAcc(ball_Vy,ball_posX,ball_posY,tools,ENEMY_POSITION_Y,op_active_card)
    my_life = tb.side['life']
    posVector = positioning(ball_Vy, ball_posY,retAcc,op_side_X,my_life)
    retCard = getCard(tb,ds,posVector,retAcc)
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, retAcc, posVector, retCard[0],retCard[1])

#待完善
def getCard(tb: TableData, ds: dict, posVector:int, retAcc:int) -> tuple:
    enemy_pos = get_opp_posY(tb.ball['velocity'].y,tb.ball['position'].y,retAcc)
    enemy_loss = (abs((DIM[3] - DIM[2])//2 - enemy_pos)**2 ) // (FACTOR_DISTANCE**2)
    for card in APP_PRRORITY:
        if card in tb.side['cards']:
            if card == CARD_INCL and tb.side['life'] < RACKET_LIFE - CARD_INCL_PARAM:
                return tb.side, card
            elif card == CARD_DECL or card == CARD_SPIN:
                return tb.op_side, card
            elif card == CARD_AMPL and enemy_loss > 800 :
                return tb.op_side, card
            elif card == CARD_TLPT and (abs(posVector)**2) // (FACTOR_DISTANCE**2) > 800 :
                return tb.side,card
            elif card == CARD_DSPR:
                return tb.side, card
    if len(tb.side['cards']) == 3 :
        minvalue = 1000000
        for var in tb.side['cards'] :
            if TOOL_VALUE[var.code] < minvalue :
                minvalue = TOOL_VALUE[var.code]
                retCard = var.code
        if retCard == CARD_TLPT or retCard == CARD_AMPL or retCard == CARD_DECL or retCard == CARD_SPIN :
            retSide = tb.op_side
        else:
            retSide = tb.side
        return retSide,retCard
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
(3):不计代价打角;(待完善)
(3):推测对方会选择对我方最不利的加速值(未考虑对方捡道具)，以此计算对方打回的球的位置，作为我方跑位的目标;
(4):综合以上三种因素加权得出最后结果，并选择跑一半(与迎球配合)
(5):缺陷:未考虑捡道具的情况,然而道具是随机出现的;
"""
def positioning(ball_Vy:int, ball_posY:int,retAcc:int,op_side_X:int,my_life:int) -> int:
    #生命值低于(RACKET_LIFE*life_factor)时,跑位选择回到中间;减少跑位太偏而'miss ball';
    if my_life < int(life_factor * RACKET_LIFE) :
        return (DIM[3] - DIM[2]) // 2 - ball_posY
    pos0 = ball_posY
    pos1 = (DIM[3]-DIM[2]) // 2
    ball_opp_posY = get_opp_posY(ball_Vy,ball_posY,retAcc)
    ball_opp_velY = ball_Vy + retAcc
    ball_opp_posX = op_side_X
    """
    #我对(对方对我方跑位的推测)的推测,intelligent为不跑，因此此处设置为ball_posY对其有优势；
    #而INDIA为跑到中间，故设置为(DIM[3]-DIM[2])//2时有优势；
    #若想要解决，则回到递归的思路上来,最终陷入“我认为他认为我认为他认为……会怎么跑位”的死循环……
    #在这个程序中，默认设定为“我认为他认为我跑位原地不动”或者"他认为我认为他跑位原地不动"，考虑两步;
    """
    #此处默认为我认为他认为我跑位原地不动:pred_of_op_pred
    pred_of_op_pred =  ball_posY
    op_side_Acc = getAcc(ball_opp_velY,ball_opp_posX,ball_opp_posY,[],pred_of_op_pred)
    pos2 = self_second_posY = get_opp_posY(ball_opp_velY,ball_opp_posY,op_side_Acc)
    pos3 = DIM[3] if ball_posY < (DIM[3]-DIM[2])//2 else DIM[2]
    pos_delta_Y = self_pos_factors[0]*(pos0-ball_posY)\
                  + self_pos_factors[1]*(pos1-ball_posY)\
                  + self_pos_factors[2]*(pos2-ball_posY)\
                  + self_pos_factors[3]*(pos3-ball_posY)
    return pos_delta_Y

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
#(未考虑对方会担心我方不计代价暴力打角而跑到角落里，待完善)
def get_opside_pos(ball_Vy,ball_posX,ball_posY,opside_posY:int) :
    pos0 = opside_posY #不跑,这是intelligent的做法，然而在参数设置[0.2,0.3,0.5]中只占了0.2,所以估计不准，优势不大
    pos1 = (DIM[3] - DIM[2]) // 2
    #此处默认为"他认为我认为他跑位原地不动":enemy_posY = opside_posY
    notools_Acc = getAcc(ball_Vy,ball_posX,ball_posY,[],opside_posY)
    pos2 = get_opp_posY(ball_Vy,ball_posY,notools_Acc)
    pos = pos0*enemy_pos_factors[0] + pos1*enemy_pos_factors[1] + pos2*enemy_pos_factors[2]
    return pos

def adjust_fac(self,enemy) :
    global self_pos_factors,enemy_pos_factors
    self_pos_factors,enemy_pos_factors = self,enemy
