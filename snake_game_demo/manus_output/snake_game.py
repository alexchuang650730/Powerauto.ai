
import pygame
import random

# 基本的遊戲設置
WINDOW_SIZE = 600
CELL_SIZE = 20

class SnakeGame:
    def __init__(self):
        self.snake = [(300, 300)]
        self.direction = (CELL_SIZE, 0)
        self.food = self.generate_food()
        
    def generate_food(self):
        return (random.randint(0, WINDOW_SIZE//CELL_SIZE-1) * CELL_SIZE,
                random.randint(0, WINDOW_SIZE//CELL_SIZE-1) * CELL_SIZE)
    
    def move(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def run(self):
        # 基本遊戲循環
        pass

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
