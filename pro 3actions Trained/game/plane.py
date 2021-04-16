import pygame
import random

# 设置游戏屏幕大小
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = init_pos
        self.speed = 14

    def move(self):
        self.rect.top -= self.speed

# 玩家飞机类
class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []                                 # 用来存储玩家飞机图片的列表
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(player_rect[i]).convert_alpha())
        self.rect = player_rect[0]                      # 初始化图片所在的矩形
        self.rect.topleft = init_pos                    # 初始化矩形的左上角坐标
        self.speed = 10                                  # 初始化玩家飞机速度，这里是一个确定的值
        self.bullets = pygame.sprite.Group()            # 玩家飞机所发射的子弹的集合
        self.is_hit = False                             # 玩家是否被击中

    # 发射子弹
    def shoot(self, bullet_img):
        bullet = Bullet(bullet_img, self.rect.midtop)
        self.bullets.add(bullet)

    # 向上移动，需要判断边界
    def moveUp(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed

    # 向下移动，需要判断边界
    def moveDown(self):
        if self.rect.top >= SCREEN_HEIGHT - self.rect.height:
            self.rect.top = SCREEN_HEIGHT - self.rect.height
        else:
            self.rect.top += self.speed

    # 向左移动，需要判断边界
    def moveLeft(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        else:
            self.rect.left -= self.speed

    # 向右移动，需要判断边界        
    def moveRight(self):
        if self.rect.left >= SCREEN_WIDTH - self.rect.width:
            self.rect.left = SCREEN_WIDTH - self.rect.width
        else:
            self.rect.left += self.speed

# 敌机类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos, speed, maxhp):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = enemy_down_imgs
        self.speed = speed
        self.hp = maxhp

    # 敌机移动，边界判断及删除在游戏主循环里处理
    def move(self):
        self.rect.top += self.speed

class GameState:

    def __init__(self):
        # 初始化 pygame
        pygame.init()
        # 设置游戏界面大小、背景图片及标题
        # 游戏界面像素大小
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 游戏界面标题
        pygame.display.set_caption('PRO 3 Actions 20Million Steps')
        # 飞机及子弹图片集合
        plane_img = pygame.image.load('game/shoot.png')
        # 设置玩家飞机不同状态的图片列表，多张图片展示为动画效果
        player_rect = []
        player_rect.append(pygame.Rect(2, 101, 98, 95))        # 玩家飞机图片 renew
        player_rect.append(pygame.Rect(165, 234, 102, 126))     # 玩家爆炸图片

        player_pos = [200, 600]
        self.player = Player(plane_img, player_rect, player_pos)
        # 子弹图片
        self.bullet_rect = pygame.Rect(1004, 987, 9, 21)
        self.bullet_img = plane_img.subsurface(self.bullet_rect)
        # 敌机不同状态的图片列表，包括正常敌机，爆炸的敌机图片
        self.enemy1_rect = pygame.Rect(539, 617, 49, 34) # renew
        self.enemy1_img = plane_img.subsurface(self.enemy1_rect)
        self.enemy1_down_imgs = plane_img.subsurface(pygame.Rect(267, 347, 57, 43))
        # Enemy2 2hp
        self.enemy2_rect = pygame.Rect(0, 3, 69, 88)
        self.enemy2_img = plane_img.subsurface(self.enemy2_rect)
        self.enemy2_down_imgs = plane_img.subsurface(pygame.Rect(535, 656, 67, 93))
        #存储敌机，管理多个对象
        self.enemies = pygame.sprite.Group()
        # 存储被击毁的飞机
        self.enemies_down = pygame.sprite.Group()
        # 存储被击中一次的2hp敌机
        self.enemies_low = pygame.sprite.Group()
        # 初始化射击及敌机移动频率
        self.shoot_frequency = 0
        self.enemy1_frequency = 0
        self.enemy2_frequency = 0
        # 初始化分数
        self.score = 0

    def frame_step(self, input_actions):
        terminal = False
        reward = 0.1
        # 控制游戏最大帧率为 30
        # 生成子弹，需要控制发射频率
        # 首先判断玩家飞机没有被击中
        # 循环15次发射一个子弹
        # 检测输入正确性
        if input_actions[0] == 1 or input_actions[1]== 1 or input_actions[2]== 1 or input_actions[3]== 1 or input_actions[4]== 1:  # 检查输入正常
            if input_actions[0] == 0 and input_actions[1] == 1 and input_actions[2] == 0:
                self.player.moveLeft()
            elif input_actions[0] == 0 and input_actions[1] == 0 and input_actions[2] == 1:
                self.player.moveRight()
            else:
                pass
        else:
            raise ValueError('Multiple input actions!')

        if not self.player.is_hit:
            if self.shoot_frequency % 15 == 0:
                self.player.shoot(self.bullet_img)
            self.shoot_frequency += 1
            if self.shoot_frequency >= 15:
                self.shoot_frequency = 0

        # 生成敌机，需要控制生成频率
        # 循环30次生成一架敌机1
        if self.enemy1_frequency % 20 == 0:
            enemy1_pos = [random.randint(0, SCREEN_WIDTH - self.enemy1_rect.width), 0]
            enemy1 = Enemy(self.enemy1_img, self.enemy1_down_imgs, enemy1_pos, 8, 1)
            self.enemies.add(enemy1)
        self.enemy1_frequency += 1
        if self.enemy1_frequency >= 100:
            self.enemy1_frequency = 0

        # 循环60次生成一架敌机2
        if self.enemy2_frequency % 70 == 0:
            enemy2_pos = [random.randint(0, SCREEN_WIDTH - self.enemy2_rect.width), 0]
            enemy2 = Enemy(self.enemy2_img, self.enemy2_down_imgs, enemy2_pos, 5, 2)
            self.enemies.add(enemy2)
        self.enemy2_frequency += 1
        if self.enemy2_frequency >= 211:
            self.enemy2_frequency = 0

        for bullet in self.player.bullets:
            # 以固定速度移动子弹
            bullet.move()
            # 移动出屏幕后删除子弹
            if bullet.rect.bottom < 0:
                self.player.bullets.remove(bullet)

        for enemy in self.enemies:
            #2. 移动敌机
            enemy.move()
            #3. 敌机与玩家飞机碰撞效果处理
            if pygame.sprite.collide_circle(enemy, self.player):
                self.enemies_down.add(enemy)
                self.enemies.remove(enemy)
                self.player.is_hit = True
                reward = -1   #撞击后退出
                terminal = True
                self.__init__()
                break
            #4. 移动出屏幕后删除敌人
            if enemy.rect.top < 0:
                self.enemies.remove(enemy)
        #敌机被子弹击中效果处理
        #将被击中的敌机对象添加到击毁敌机 Group 中
        enemies_hitted = pygame.sprite.groupcollide(self.enemies, self.player.bullets, 0, 1) # 碰撞之后子弹消失，敌机不变
        for enemy in enemies_hitted:
            enemy.hp -= 1
            if enemy.hp != 0:
                reward = 0.5
            if enemy.hp == 0:
                self.score += 1
                #self.screen.blit(enemy_down.down_imgs, enemy_down.rect)  # 将爆炸的敌机画出来
                reward = 1
                self.enemies.remove(enemy) # 血量为0时删除敌机

        # 绘制背景
        self.screen.fill(0)
        # screen.blit(background, (0, 0))

        # 绘制玩家飞机
        if not self.player.is_hit:
            self.screen.blit(self.player.image[0], self.player.rect) #将正常飞机画出来
        else:
            # 玩家飞机被击中后的效果处理
            self.screen.blit(self.player.image[1], self.player.rect) #将爆炸的飞机画出来


        # 显示子弹
        self.player.bullets.draw(self.screen)
        # 显示敌机
        self.enemies.draw(self.screen)
        #self.enemies_low.draw(self.screen)

        # 绘制得分
        score_font = pygame.font.Font(None, 36)
        # score_text = score_font.render('score: '+str(score), True, (128, 128, 128))
        score_text = score_font.render(str(self.score), True, (128, 128, 128))

        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        self.screen.fill((0, 0, 0), text_rect)
        self.screen.blit(score_text, text_rect)

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.update()
        clock = pygame.time.Clock()
        clock.tick(30)
        return image_data, reward, terminal