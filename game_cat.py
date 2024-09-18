import pygame
import sys
import random
from datetime import timedelta
import json

# 初始化Pygame
pygame.init()
score = 0
TILE_SIZE = 100  #图片大小
spacing = 30  #图片间隔
game_over=False
flag = False
MAX_LEADERBOARD_LENGTH=5
k = 0
j = 0

WHITE = (0, 0, 0)

# 设定游戏时长（毫秒）
GAME_DURATION = 30000  # 30秒
# 设定游戏时长（毫秒）
GAME_DURATION_hard = 120000  # 120秒

# 初始化游戏开始时间
start_time = 0

# 设置屏幕尺寸
screen_width = 800
screen_height = 690
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("羊了个羊（猫猫版）")

# 加载图片（如果需要）
start_bg = pygame.image.load('游戏背景.png')  # 替换为你的图片路径
start_bg = pygame.transform.scale(start_bg, (screen_width, screen_height))
start_2 = pygame.image.load('背景4.png')  # 替换为你的图片路径
start_2 = pygame.transform.scale(start_2, (screen_width, screen_height))
game_bg = pygame.image.load('背景3.png')  # 替换为你的图片路径
game_bg = pygame.transform.scale(game_bg, (screen_width, screen_height))
phb = pygame.image.load('排行榜.png')  # 替换为你的图片路径
phb = pygame.transform.scale(phb, (screen_width, screen_height))
game_overbg = pygame.image.load('分数显示2.png')  # 替换为你的图片路径
game_overbg = pygame.transform.scale(game_overbg, (screen_width, screen_height))

# 加载图案图片
patterns = [pygame.image.load(f"图片{i}.png") for i in range(1, 6)]
patterns = [pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE)) for p in patterns]

# 创建游戏板
board_width = screen_width // (TILE_SIZE+spacing)
board_height = screen_height // (TILE_SIZE+spacing)

#一维列表
board1 = [[random.choice(patterns) for _ in range(board_width)] for _ in range(board_height)]
# board2是一个二维列表的列表，每个内部二维列表代表一层
board2 = [[[random.choice(patterns) for _ in range(board_width)] for _ in range(board_height)] for _ in range(2)]
# 注意：现在board[0]是底层，board[1]是上层

# 收集框
collection = []
max_collection_size = 5

# 撤销历史列表
undo_history = []
undo_history_hard = []

# 设置字体
font = pygame.font.Font('SimHei.ttf', 36)  # 使用中文字体
font_title = pygame.font.Font('SimHei.ttf', 40)  # 使用中文字体

# 游戏状态
class GameState:
    START = 0
    SELECT_MODE = 1
    RANKING = 2
    EASY_MODE = 3
    HARD_MODE = 4
    GAME_OVER = 5

def draw_board_easy():
    # 初始化起始位置（考虑间隔）
    x_start = 20  # 通常不需要为第一列添加额外的x间隔
    y_start = 0  # 如果需要为第一行上方留出空间，可以在这里调整y_start
    row1 =board_height
    for col in range(board_width):
        board1[0][col] = None
        board1[row1-1][col] = None
    # 遍历每一行
    for row in range(1,board_height-1):
        x_pos = x_start  # 重置每行的x位置
        # 遍历每一列
        for col in range(board_width):
            if board1[row][col] is not None:
                tile = board1[row][col]

                # 绘制瓷砖，并考虑间隔
                screen.blit(tile, (x_pos, y_start + row * (TILE_SIZE + spacing)))

                # 更新x位置以准备下一个瓷砖（包括间隔）
            x_pos += TILE_SIZE + spacing

def draw_board_hard():
    for layer in range(2):  # 遍历两层
        for row in range(board_height):
            for col in range(board_width):
                if row==0 or row==board_height-1:
                    board2[layer][row][col]=None
                else:
                    # 计算每个瓷砖的位置
                    x = col * (TILE_SIZE + spacing) +30# 假设spacing是瓷砖之间的间隔
                    y = row * (TILE_SIZE + spacing + 10) + layer * (TILE_SIZE // 5)  # 上层稍微向下偏移

                    # 绘制瓷砖
                    if board2[layer][row][col] is not None:
                        screen.blit(board2[layer][row][col], (x, y))


# 检查收集框中是否有三张相同图片
def check_for_three_of_a_kind(collection):
    from collections import defaultdict
    image_count = defaultdict(int)  # 使用字典统计每种图片的数量

    # 遍历收集框中的图片，并计数
    for img in collection:
        image_count[id(img)] += 1

    # 检查是否有三种或更多相同图片
    images_to_remove = set()
    for img_id, count in image_count.items():
        if count >= 3:
            images_to_remove.add(img_id)

    # 移除收集框中的重复图片
    new_collection = [img for img in collection if id(img) not in images_to_remove]

    return new_collection, len(collection) - len(new_collection)  # 返回新的收集框和消除的图片数量


# 初始状态
current_state = GameState.START


# 排行榜
leaderboard = []

# 读取排行榜数据（如果有）
try:
    with open('leaderboard.json', 'r') as f:
        leaderboard = json.load(f)
except FileNotFoundError:
    pass

#清空排行榜
def clear_leaderboard_file():
    with open('leaderboard.json', 'w') as f:
        json.dump([], f)

# 写入排行榜数据
def save_leaderboard():
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)

# 游戏主循环
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if current_state == GameState.START:
                if 300 <= mouse_pos[0] <= 500 and 200 <= mouse_pos[1] <= 250:
                    current_state = GameState.SELECT_MODE
                elif 300 <= mouse_pos[0] <= 500 and 300 <= mouse_pos[1] <= 350:
                    current_state = GameState.RANKING
                elif 300 <= mouse_pos[0] <= 500 and 400 <= mouse_pos[1] <= 450:
                    running = False
            elif current_state == GameState.SELECT_MODE:
                if 300 <= mouse_pos[0] <= 500 and 200 <= mouse_pos[1] <= 250:
                    current_state = GameState.EASY_MODE
                elif 300 <= mouse_pos[0] <= 500 and 300 <= mouse_pos[1] <= 350:
                    current_state = GameState.HARD_MODE
            elif current_state == GameState.RANKING:
                if 300 <= mouse_pos[0] <= 500 and 470 <= mouse_pos[1] <= 520:
                    current_state = GameState.START
            elif current_state == GameState.GAME_OVER:
                if 300 <= mouse_pos[0] <= 500 and 300 <= mouse_pos[1] <= 350:
                    current_state = GameState.START
                    game_over = False
                    score = 0
                    collection = []
                    flag = True  # 这将导致游戏板在下一次循环开始时被重置
                elif 300 <= mouse_pos[0] <= 500 and 400 <= mouse_pos[1] <= 450:
                    current_state = GameState.EASY_MODE if game_mode == GameState.EASY_MODE else GameState.HARD_MODE
                    game_over = False
                    score = 0
                    collection = []
                    flag = True  # 这将导致游戏板在下一次循环开始时被重置
                    #board1 = [[None for _ in range(board_width)] for _ in range(board_height)]  # 清空游戏板

    #screen.fill((255, 255, 255))

    pygame.display.flip()

    if current_state == GameState.START:
        # 开始界面
        screen.blit(start_bg, (0, 0))  # 如果需要背景图片
        title_text = font_title.render("羊了个羊（猫猫版）(=^･ω･^=) ", True, (220, 160, 214))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))
        #screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))

        for i in range(4):
            pygame.draw.circle(screen,(218,112,214) , (320+i*54, 223), 26)

        easy_button = font.render("模 式 选 择", True,(255, 255, 255))
        screen.blit(easy_button, (300, 200))

        for i in range(3):
            pygame.draw.circle(screen, (112,214,11), (322+i*50, 323), 25)
        #pygame.draw.rect(screen, (0,201,87), (300, 300, 150, 50))
        ranking_button = font.render("排 行 榜", True, (255, 255, 255))
        screen.blit(ranking_button, (300, 300))

        for i in range(4):
            pygame.draw.circle(screen, (127, 224, 212), (320+i*54, 423), 26)
        #pygame.draw.rect(screen, (127, 224, 212), (300, 400, 150, 50))
        exit_button = font.render("退 出 游 戏", True, (255, 255, 255))
        screen.blit(exit_button, (300, 400))

    elif current_state == GameState.SELECT_MODE:
        # 模式选择界面
        screen.blit(start_2, (0, 0))  # 如果需要背景图片
        title_text = font_title.render("选择模式", True, (255, 255, 255))
        screen.blit(title_text, (300, 100))
        #screen_width // 2 - title_text.get_width() // 2
        easy_button = font.render("简单模式", True, (255, 255, 255))
        screen.blit(easy_button, (300, 200))

        hard_button = font.render("困难模式", True, (255, 255, 255))
        screen.blit(hard_button, (300, 300))

    elif current_state == GameState.RANKING:
        # 排行榜界面
        screen.blit(phb, (0, 0))  # 如果需要背景图片
        title_text = font.render("排行榜", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))
        back_button = font.render("返回开始界面", True, (255, 255, 255))
        screen.blit(back_button, (300, 470))

        # 排序排行榜
        #leaderboard.sort(key=lambda x: x['score'])

        # 显示排行榜
        for i, entry in enumerate(leaderboard):
            rank_text = font.render(f"{i + 1}. {entry['name']}: {entry['score']}", True, (255, 255, 255))
            screen.blit(rank_text, (screen_width /2 -90, 160+ i * 65))


    #简单模式游戏逻辑
    elif current_state == GameState.EASY_MODE:
        screen.blit(game_bg, (0, 0))  # 如果需要背景图片
        remaining_time=0
        game_mode = GameState.EASY_MODE if current_state == GameState.EASY_MODE else GameState.HARD_MODE
        #看看是不是重新开始游戏
        if flag:
            board1 = [[random.choice(patterns) for _ in range(board_width)] for _ in range(board_height)]
            start_time = pygame.time.get_ticks()  # 记录游戏开始时间
            flag = False
            pygame.display.flip()
            draw_board_easy()
        game_over = False
        while not game_over:
            # 计算剩余时间
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = GAME_DURATION - elapsed_time
            # 检查时间是否耗尽
            if remaining_time <= 0:
                game_over = True
                #game_over = True  # 立即设置游戏状态为结束

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 处理鼠标点击事件
                    mouse_pos = pygame.mouse.get_pos()
                    if 600 <= mouse_pos[0] <= 800 and 50 <= mouse_pos[1] <= 100:
                        # 取出最后一个操作
                        img, (row, col) = undo_history.pop()

                        # 将图案从收集框中移除（需要跟踪或搜索）
                        for i, c_img in enumerate(collection):
                            if c_img == img:
                                del collection[i]
                                break

                                # 将图案放回棋盘
                        board1[row][col] = img

                    else:
                        # 简化处理：点击网格区域
                        x, y = mouse_pos[0] // (TILE_SIZE + spacing), mouse_pos[1] // (TILE_SIZE + spacing)
                        if 0 <= x < board_width and 0 <= y < board_height and board1[y][x] is not None:
                            # 将图片添加到收集框，并清除网格中的图片
                            undo_history.append((board1[y][x], (y, x)))  #加入撤销操作
                            collection.append(board1[y][x])
                            board1[y][x] = None  # y应该是行索引而x是列索引

                            # 检查是否三张相同图片在收集框中
                        collection, removed_images = check_for_three_of_a_kind(collection)
                        score += removed_images

                        # 检查游戏是否结束
                        if all(cell is None for row in board1 for cell in row) or len(
                                collection) == max_collection_size or remaining_time <= 0:
                            game_over = True

            if game_over:
                k = k + 1
                new_score = {'name': f'简单{k}', 'score': score, 'difficulty': 'easy'}
                current_state = GameState.GAME_OVER

            # 绘制游戏界面
            screen.blit(game_bg, (0, 0))  # 如果需要背景图片

            reback_button = font.render("撤销", True, (0, 0, 0))
            screen.blit(reback_button, (screen_width-100, 50))


            # 绘制分数和时间（这里用帧数模拟）
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 40))

            # 显示剩余时间
            if (remaining_time // 1000) <= 10:
                time_text = font_title.render(f"Time Left: {remaining_time // 1000}s", True, (255,64,64))
            else:
                time_text = font.render(f"Time Left: {remaining_time // 1000}s", True, WHITE)

            screen.blit(time_text, (screen_width - 400, 40))  # 假设显示在屏幕右上角

            # 更新网格
            draw_board_easy()

            # 如果游戏没有结束，绘制收集框和其中的图片
            if not game_over:
                # 绘制收集框（简化处理：只绘制在屏幕底部）
                collection_x = 10  # 收集框的起始X坐标
                collection_y = screen_height - TILE_SIZE - 20  # 收集框的起始Y坐标（留出一些空间）
                newsit = screen_width / 5

                for i, img in enumerate(collection):
                    # 计算图片的绘制位置
                    x = collection_x +i* newsit
                    y = collection_y

                    screen.blit(img, (x, y))

            pygame.display.flip()
            clock.tick(10)  # 控制游戏帧率

        # 处理困难模式的游戏逻辑
    elif current_state == GameState.HARD_MODE:
        screen.blit(game_bg, (0, 0))
        remaining_time = 0
        game_mode = GameState.EASY_MODE if current_state == GameState.EASY_MODE else GameState.HARD_MODE
        if flag:
            board2 = [[[random.choice(patterns) for _ in range(board_width)] for _ in range(board_height)] for _ in range(2)]
            start_time = pygame.time.get_ticks()  # 记录游戏开始时间
            flag = False
            draw_board_hard()
        game_over = False
        while not game_over:
            # 计算剩余时间
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = GAME_DURATION_hard - elapsed_time
            # 检查时间是否耗尽
            if remaining_time <= 0:
                game_over = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 处理鼠标点击事件
                    mouse_pos = pygame.mouse.get_pos()
                    if 600 <= mouse_pos[0] <= 800 and 50 <= mouse_pos[1] <= 100:
                        #undo_history:
                        img, (layer, row, col) = undo_history_hard.pop()  # 假设layer是0或1，表示上层或下层
                        if img in collection:
                            collection.remove(img)
                            # 将图片放回原来的层
                            if layer == 0:
                                board2[0][row][col] = img
                                board2[1][row][col] = None  # 如果需要确保上层为空
                            elif layer == 1:
                                board2[1][row][col] = img
                                # 通常不需要将下层设置为None，因为下层可能有其他图片

                    else:
                        # 简化处理：点击网格区域
                        x, y = mouse_pos[0] // (TILE_SIZE + spacing), mouse_pos[1] // (TILE_SIZE + spacing)
                        if 0 <= x < board_width and 0 <= y < board_height:
                            # 检查上层是否有图片，如果有则消除上层图片
                            if board2[1][y][x] is not None:
                                undo_history_hard.append((board2[1][y][x], (1,y, x)))
                                collection.append(board2[1][y][x])
                                board2[1][y][x] = None
                            # 如果上层没有图片并且下层有图片，则消除下层图片
                            elif board2[0][y][x] is not None:
                                undo_history_hard.append((board2[0][y][x], (0,y, x)))
                                collection.append(board2[0][y][x])
                                board2[0][y][x] = None

                            # 检查是否三张相同图片在收集框中
                            collection, removed_images = check_for_three_of_a_kind(collection)
                            score += removed_images

                            # 检查游戏是否结束
                            if all(cell is None for row in board2[1] for cell in row) and \
                                    all(cell is None for row in board2[0] for cell in row) or \
                                    len(collection) == max_collection_size:
                                game_over = True
                if game_over:
                    j = j + 1
                    new_score = {'name': f"困难{j}", 'score': score, 'difficulty': 'hard'}
                    current_state = GameState.GAME_OVER

                                # 绘制游戏界面
            # screen.fill(BLACK)
            screen.blit(game_bg, (0, 0))  # 如果需要背景图片

            reback_button = font.render("撤销", True, (0, 0, 0))
            screen.blit(reback_button, (screen_width - 100, 50))

            # 绘制分数和时间（这里用帧数模拟）
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 40))

            # 显示剩余时间
            if (remaining_time // 1000) <= 30:
                time_text = font_title.render(f"Time Left: {remaining_time // 1000}s", True, (255, 64, 64))
            else:
                time_text = font.render(f"Time Left: {remaining_time // 1000}s", True, WHITE)
            screen.blit(time_text, (screen_width - 400, 40))  # 假设显示在屏幕右上角

            # 更新网格
            draw_board_hard()

            # 如果游戏没有结束，绘制收集框和其中的图片
            if not game_over:
                # 绘制收集框（简化处理：只绘制在屏幕底部）
                collection_x = 10  # 收集框的起始X坐标
                collection_y = screen_height - TILE_SIZE - 20  # 收集框的起始Y坐标（留出一些空间）
                newsit = screen_width / 5
                for i, img in enumerate(collection):
                    # 计算图片的绘制位置
                    x = collection_x + i * newsit
                    y = collection_y

                    # 绘制图片
                    screen.blit(img, (x, y))

            pygame.display.flip()
            clock.tick(10)  # 控制游戏帧率

    elif current_state == GameState.GAME_OVER:
        # 游戏结束界面
        screen.blit(game_overbg, (0, 0))  # 如果需要背景图片
        # 检查是否需要添加这个分数
        add_to_leaderboard = True

        if add_to_leaderboard:
            # 检查是否已存在相同的名称
            existing_score = next((s for s in leaderboard if s['name'] == new_score['name']), None)
            if not existing_score:
                # 添加新分数到排行榜
                leaderboard.append(new_score)
                # 排序排行榜，首先按分数降序，然后按难度排序（"hard" 在前，"easy" 在后）
                leaderboard.sort(key=lambda x: (-x['score'], ('hard', 'easy').index(x['difficulty'])))
                # 如果排行榜长度超过最大限制，则截断
                if len(leaderboard) > MAX_LEADERBOARD_LENGTH:
                    leaderboard = leaderboard[:MAX_LEADERBOARD_LENGTH]

                    # 保存排行榜数据
        save_leaderboard()


        if game_mode == GameState.EASY_MODE or game_mode == GameState.HARD_MODE:
            if all(cell is None for row in board1 for cell in row) or all(
                    cell is None for row in board2[0] for cell in row) and all(
                    cell is None for row in board2[1] for cell in row):
                game_over_text = font_title.render("游戏胜利", True, (255, 255, 255))
            else:
                game_over_text = font_title.render("猫猫没有全部回家呢", True, (255, 255, 255))

            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 50))

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 200))

            back_button = font.render("返回开始界面", True, (255, 255, 255))
            screen.blit(back_button, (300, 300))

            retry_button = font.render("再来一次", True, (255, 255, 255))
            screen.blit(retry_button, (300, 400))

        #pygame.display.flip()
        #clock.tick(60)  # 控制游戏帧率


# 清除排行榜数据
clear_leaderboard_file()

# 退出Pygame
pygame.quit()
sys.exit()