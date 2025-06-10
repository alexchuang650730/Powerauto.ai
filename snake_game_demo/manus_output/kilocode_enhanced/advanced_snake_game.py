#!/usr/bin/env python3
"""
高難度貪吃蛇遊戲 - KiloCode增強版

特性：
- 多難度級別
- 特殊道具系統
- 障礙物生成
- 高分記錄
- 平滑動畫
- 音效支持
"""

import pygame
import random
import json
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# 遊戲常數
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
FPS = 60

# 顏色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    NIGHTMARE = 4

class PowerUpType(Enum):
    SPEED_BOOST = "speed_boost"
    SLOW_TIME = "slow_time"
    DOUBLE_SCORE = "double_score"
    INVINCIBLE = "invincible"
    SHRINK = "shrink"

@dataclass
class PowerUp:
    x: int
    y: int
    type: PowerUpType
    duration: int
    color: Tuple[int, int, int]

@dataclass
class Obstacle:
    x: int
    y: int
    width: int
    height: int

class AdvancedSnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("高難度貪吃蛇遊戲 - KiloCode版")
        self.clock = pygame.time.Clock()
        
        # 遊戲狀態
        self.running = True
        self.game_over = False
        self.paused = False
        
        # 難度設置
        self.difficulty = Difficulty.MEDIUM
        self.base_speed = self.get_speed_for_difficulty()
        self.current_speed = self.base_speed
        
        # 蛇的初始化
        self.snake = [(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)]
        self.direction = (CELL_SIZE, 0)
        self.next_direction = (CELL_SIZE, 0)
        
        # 食物和道具
        self.food = self.generate_food()
        self.power_ups: List[PowerUp] = []
        self.active_effects = {}
        
        # 障礙物（高難度模式）
        self.obstacles: List[Obstacle] = []
        if self.difficulty.value >= 3:
            self.generate_obstacles()
        
        # 分數和統計
        self.score = 0
        self.high_score = self.load_high_score()
        self.food_eaten = 0
        
        # 視覺效果
        self.particle_effects = []
        self.screen_shake = 0
        
        # 音效（如果可用）
        self.init_sounds()
        
        # 字體
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def get_speed_for_difficulty(self) -> int:
        speeds = {
            Difficulty.EASY: 8,
            Difficulty.MEDIUM: 12,
            Difficulty.HARD: 16,
            Difficulty.NIGHTMARE: 20
        }
        return speeds[self.difficulty]
    
    def init_sounds(self):
        try:
            pygame.mixer.init()
            # 這裡可以加載音效文件
            self.sounds = {
                'eat': None,  # pygame.mixer.Sound('eat.wav')
                'power_up': None,  # pygame.mixer.Sound('powerup.wav')
                'game_over': None  # pygame.mixer.Sound('gameover.wav')
            }
        except:
            self.sounds = {}
    
    def generate_food(self) -> Tuple[int, int]:
        while True:
            x = random.randint(0, (WINDOW_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            
            # 確保食物不在蛇身上或障礙物上
            if (x, y) not in self.snake and not self.is_obstacle_collision(x, y):
                return (x, y)
    
    def generate_obstacles(self):
        obstacle_count = self.difficulty.value * 2
        for _ in range(obstacle_count):
            width = random.randint(2, 4) * CELL_SIZE
            height = random.randint(2, 4) * CELL_SIZE
            x = random.randint(0, (WINDOW_WIDTH - width) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - height) // CELL_SIZE) * CELL_SIZE
            
            self.obstacles.append(Obstacle(x, y, width, height))
    
    def generate_power_up(self):
        if random.random() < 0.1:  # 10%機率生成道具
            power_type = random.choice(list(PowerUpType))
            x = random.randint(0, (WINDOW_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            
            colors = {
                PowerUpType.SPEED_BOOST: YELLOW,
                PowerUpType.SLOW_TIME: BLUE,
                PowerUpType.DOUBLE_SCORE: PURPLE,
                PowerUpType.INVINCIBLE: ORANGE,
                PowerUpType.SHRINK: WHITE
            }
            
            power_up = PowerUp(x, y, power_type, 300, colors[power_type])
            self.power_ups.append(power_up)
    
    def is_obstacle_collision(self, x: int, y: int) -> bool:
        for obstacle in self.obstacles:
            if (obstacle.x <= x < obstacle.x + obstacle.width and
                obstacle.y <= y < obstacle.y + obstacle.height):
                return True
        return False
    
    def update_snake(self):
        if self.game_over or self.paused:
            return
        
        # 更新方向
        self.direction = self.next_direction
        
        # 計算新頭部位置
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 邊界檢測
        if (new_head[0] < 0 or new_head[0] >= WINDOW_WIDTH or
            new_head[1] < 0 or new_head[1] >= WINDOW_HEIGHT):
            if 'invincible' not in self.active_effects:
                self.end_game()
                return
        
        # 自身碰撞檢測
        if new_head in self.snake and 'invincible' not in self.active_effects:
            self.end_game()
            return
        
        # 障礙物碰撞檢測
        if (self.is_obstacle_collision(new_head[0], new_head[1]) and 
            'invincible' not in self.active_effects):
            self.end_game()
            return
        
        # 添加新頭部
        self.snake.insert(0, new_head)
        
        # 檢查是否吃到食物
        if new_head == self.food:
            self.eat_food()
        else:
            self.snake.pop()
        
        # 檢查道具碰撞
        self.check_power_up_collision()
        
        # 更新活躍效果
        self.update_active_effects()
    
    def eat_food(self):
        self.score += 10 * (1 + self.difficulty.value)
        if 'double_score' in self.active_effects:
            self.score += 10 * (1 + self.difficulty.value)
        
        self.food_eaten += 1
        self.food = self.generate_food()
        
        # 增加遊戲速度
        if self.food_eaten % 5 == 0:
            self.current_speed = min(self.current_speed + 1, 25)
        
        # 生成道具
        self.generate_power_up()
        
        # 添加粒子效果
        self.add_particle_effect(self.snake[0], GREEN)
        
        # 播放音效
        if 'eat' in self.sounds and self.sounds['eat']:
            self.sounds['eat'].play()
    
    def check_power_up_collision(self):
        head = self.snake[0]
        for power_up in self.power_ups[:]:
            if head == (power_up.x, power_up.y):
                self.activate_power_up(power_up)
                self.power_ups.remove(power_up)
    
    def activate_power_up(self, power_up: PowerUp):
        effect_duration = 180  # 3秒 (60 FPS)
        
        if power_up.type == PowerUpType.SPEED_BOOST:
            self.current_speed += 5
            self.active_effects['speed_boost'] = effect_duration
        elif power_up.type == PowerUpType.SLOW_TIME:
            self.current_speed = max(self.current_speed - 5, 3)
            self.active_effects['slow_time'] = effect_duration
        elif power_up.type == PowerUpType.DOUBLE_SCORE:
            self.active_effects['double_score'] = effect_duration
        elif power_up.type == PowerUpType.INVINCIBLE:
            self.active_effects['invincible'] = effect_duration
        elif power_up.type == PowerUpType.SHRINK:
            if len(self.snake) > 3:
                self.snake = self.snake[:len(self.snake)//2]
        
        # 添加粒子效果
        self.add_particle_effect((power_up.x, power_up.y), power_up.color)
        
        # 播放音效
        if 'power_up' in self.sounds and self.sounds['power_up']:
            self.sounds['power_up'].play()
    
    def update_active_effects(self):
        for effect in list(self.active_effects.keys()):
            self.active_effects[effect] -= 1
            if self.active_effects[effect] <= 0:
                del self.active_effects[effect]
                
                # 恢復原始效果
                if effect == 'speed_boost':
                    self.current_speed = self.base_speed
                elif effect == 'slow_time':
                    self.current_speed = self.base_speed
    
    def add_particle_effect(self, position: Tuple[int, int], color: Tuple[int, int, int]):
        for _ in range(10):
            particle = {
                'x': position[0] + CELL_SIZE // 2,
                'y': position[1] + CELL_SIZE // 2,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': 30,
                'color': color
            }
            self.particle_effects.append(particle)
    
    def update_particle_effects(self):
        for particle in self.particle_effects[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particle_effects.remove(particle)
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.restart_game()
                    else:
                        self.paused = not self.paused
                elif not self.game_over and not self.paused:
                    if event.key == pygame.K_UP and self.direction != (0, CELL_SIZE):
                        self.next_direction = (0, -CELL_SIZE)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -CELL_SIZE):
                        self.next_direction = (0, CELL_SIZE)
                    elif event.key == pygame.K_LEFT and self.direction != (CELL_SIZE, 0):
                        self.next_direction = (-CELL_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-CELL_SIZE, 0):
                        self.next_direction = (CELL_SIZE, 0)
    
    def render(self):
        # 清除螢幕
        self.screen.fill(BLACK)
        
        # 螢幕震動效果
        offset_x = offset_y = 0
        if self.screen_shake > 0:
            offset_x = random.randint(-self.screen_shake, self.screen_shake)
            offset_y = random.randint(-self.screen_shake, self.screen_shake)
            self.screen_shake -= 1
        
        # 繪製障礙物
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, WHITE, 
                           (obstacle.x + offset_x, obstacle.y + offset_y, 
                            obstacle.width, obstacle.height))
        
        # 繪製蛇
        for i, segment in enumerate(self.snake):
            color = GREEN
            if 'invincible' in self.active_effects:
                # 無敵狀態閃爍效果
                color = YELLOW if (pygame.time.get_ticks() // 100) % 2 else GREEN
            
            # 蛇頭稍微大一點
            size = CELL_SIZE if i > 0 else CELL_SIZE - 2
            pygame.draw.rect(self.screen, color,
                           (segment[0] + offset_x + (CELL_SIZE - size) // 2,
                            segment[1] + offset_y + (CELL_SIZE - size) // 2,
                            size, size))
        
        # 繪製食物
        pygame.draw.rect(self.screen, RED,
                        (self.food[0] + offset_x, self.food[1] + offset_y,
                         CELL_SIZE, CELL_SIZE))
        
        # 繪製道具
        for power_up in self.power_ups:
            pygame.draw.circle(self.screen, power_up.color,
                             (power_up.x + CELL_SIZE // 2 + offset_x,
                              power_up.y + CELL_SIZE // 2 + offset_y),
                             CELL_SIZE // 2)
        
        # 繪製粒子效果
        for particle in self.particle_effects:
            alpha = int(255 * (particle['life'] / 30))
            color = (*particle['color'], alpha)
            pygame.draw.circle(self.screen, particle['color'][:3],
                             (int(particle['x']) + offset_x,
                              int(particle['y']) + offset_y), 2)
        
        # 繪製UI
        self.render_ui()
        
        # 遊戲結束畫面
        if self.game_over:
            self.render_game_over()
        
        # 暫停畫面
        if self.paused:
            self.render_pause()
        
        pygame.display.flip()
    
    def render_ui(self):
        # 分數
        score_text = self.font.render(f"分數: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 最高分
        high_score_text = self.small_font.render(f"最高分: {self.high_score}", True, WHITE)
        self.screen.blit(high_score_text, (10, 50))
        
        # 難度
        difficulty_text = self.small_font.render(f"難度: {self.difficulty.name}", True, WHITE)
        self.screen.blit(difficulty_text, (10, 75))
        
        # 活躍效果
        y_offset = 100
        for effect in self.active_effects:
            effect_text = self.small_font.render(f"{effect}: {self.active_effects[effect]//60}s", True, YELLOW)
            self.screen.blit(effect_text, (10, y_offset))
            y_offset += 25
    
    def render_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("遊戲結束!", True, RED)
        score_text = self.font.render(f"最終分數: {self.score}", True, WHITE)
        restart_text = self.small_font.render("按空白鍵重新開始", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def render_pause(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("遊戲暫停", True, WHITE)
        text_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)
    
    def end_game(self):
        self.game_over = True
        self.screen_shake = 10
        
        # 更新最高分
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        
        # 播放遊戲結束音效
        if 'game_over' in self.sounds and self.sounds['game_over']:
            self.sounds['game_over'].play()
    
    def restart_game(self):
        self.__init__()
    
    def load_high_score(self) -> int:
        try:
            with open('high_score.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def run(self):
        frame_count = 0
        
        while self.running:
            self.handle_input()
            
            # 根據速度控制更新頻率
            if frame_count % (FPS // self.current_speed) == 0:
                self.update_snake()
            
            self.update_particle_effects()
            self.render()
            self.clock.tick(FPS)
            frame_count += 1
        
        pygame.quit()

if __name__ == "__main__":
    game = AdvancedSnakeGame()
    game.run()
