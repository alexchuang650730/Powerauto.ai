// 高性能貪吃蛇遊戲核心邏輯 - KiloCode增強版

class GameEngine {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.lastTime = 0;
        this.accumulator = 0;
        this.fixedTimeStep = 1000 / 60; // 60 FPS
        
        // 性能優化
        this.offscreenCanvas = document.createElement('canvas');
        this.offscreenCtx = this.offscreenCanvas.getContext('2d');
        this.setupOffscreenCanvas();
    }
    
    setupOffscreenCanvas() {
        this.offscreenCanvas.width = this.canvas.width;
        this.offscreenCanvas.height = this.canvas.height;
    }
    
    gameLoop(currentTime) {
        const deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;
        
        this.accumulator += deltaTime;
        
        while (this.accumulator >= this.fixedTimeStep) {
            this.update(this.fixedTimeStep);
            this.accumulator -= this.fixedTimeStep;
        }
        
        this.render();
        requestAnimationFrame((time) => this.gameLoop(time));
    }
    
    update(deltaTime) {
        // 遊戲邏輯更新
    }
    
    render() {
        // 雙緩衝渲染
        this.offscreenCtx.clearRect(0, 0, this.offscreenCanvas.width, this.offscreenCanvas.height);
        
        // 在離屏畫布上繪製
        this.renderGame(this.offscreenCtx);
        
        // 將離屏畫布複製到主畫布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.offscreenCanvas, 0, 0);
    }
    
    renderGame(ctx) {
        // 具體的遊戲渲染邏輯
    }
}

class AISnakeController {
    constructor(game) {
        this.game = game;
        this.pathfinding = new AStarPathfinding();
    }
    
    calculateNextMove() {
        const head = this.game.snake[0];
        const food = this.game.food;
        
        // 使用A*算法尋找最佳路徑
        const path = this.pathfinding.findPath(
            head, 
            food, 
            this.game.obstacles,
            this.game.snake
        );
        
        if (path.length > 1) {
            const nextPos = path[1];
            return this.getDirectionFromPositions(head, nextPos);
        }
        
        // 如果找不到路徑，使用安全移動策略
        return this.getSafeDirection();
    }
    
    getDirectionFromPositions(from, to) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        
        if (dx > 0) return {x: 1, y: 0};
        if (dx < 0) return {x: -1, y: 0};
        if (dy > 0) return {x: 0, y: 1};
        if (dy < 0) return {x: 0, y: -1};
        
        return {x: 0, y: 0};
    }
    
    getSafeDirection() {
        const head = this.game.snake[0];
        const directions = [
            {x: 1, y: 0},
            {x: -1, y: 0},
            {x: 0, y: 1},
            {x: 0, y: -1}
        ];
        
        for (let dir of directions) {
            const newPos = {
                x: head.x + dir.x,
                y: head.y + dir.y
            };
            
            if (this.isSafePosition(newPos)) {
                return dir;
            }
        }
        
        return directions[0]; // 最後手段
    }
    
    isSafePosition(pos) {
        // 檢查邊界
        if (pos.x < 0 || pos.x >= this.game.canvas.width / this.game.gridSize ||
            pos.y < 0 || pos.y >= this.game.canvas.height / this.game.gridSize) {
            return false;
        }
        
        // 檢查蛇身
        if (this.game.snake.some(segment => segment.x === pos.x && segment.y === pos.y)) {
            return false;
        }
        
        // 檢查障礙物
        for (let obstacle of this.game.obstacles) {
            if (pos.x >= obstacle.x && pos.x < obstacle.x + obstacle.width &&
                pos.y >= obstacle.y && pos.y < obstacle.y + obstacle.height) {
                return false;
            }
        }
        
        return true;
    }
}

class AStarPathfinding {
    findPath(start, goal, obstacles, snake) {
        const openSet = [start];
        const closedSet = [];
        const cameFrom = new Map();
        const gScore = new Map();
        const fScore = new Map();
        
        gScore.set(this.posToString(start), 0);
        fScore.set(this.posToString(start), this.heuristic(start, goal));
        
        while (openSet.length > 0) {
            // 找到fScore最小的節點
            let current = openSet.reduce((min, pos) => 
                fScore.get(this.posToString(pos)) < fScore.get(this.posToString(min)) ? pos : min
            );
            
            if (current.x === goal.x && current.y === goal.y) {
                return this.reconstructPath(cameFrom, current);
            }
            
            openSet.splice(openSet.indexOf(current), 1);
            closedSet.push(current);
            
            for (let neighbor of this.getNeighbors(current)) {
                if (this.isBlocked(neighbor, obstacles, snake) || 
                    closedSet.some(pos => pos.x === neighbor.x && pos.y === neighbor.y)) {
                    continue;
                }
                
                const tentativeGScore = gScore.get(this.posToString(current)) + 1;
                
                if (!openSet.some(pos => pos.x === neighbor.x && pos.y === neighbor.y)) {
                    openSet.push(neighbor);
                } else if (tentativeGScore >= gScore.get(this.posToString(neighbor))) {
                    continue;
                }
                
                cameFrom.set(this.posToString(neighbor), current);
                gScore.set(this.posToString(neighbor), tentativeGScore);
                fScore.set(this.posToString(neighbor), tentativeGScore + this.heuristic(neighbor, goal));
            }
        }
        
        return []; // 找不到路徑
    }
    
    getNeighbors(pos) {
        return [
            {x: pos.x + 1, y: pos.y},
            {x: pos.x - 1, y: pos.y},
            {x: pos.x, y: pos.y + 1},
            {x: pos.x, y: pos.y - 1}
        ];
    }
    
    isBlocked(pos, obstacles, snake) {
        // 檢查邊界
        if (pos.x < 0 || pos.x >= 30 || pos.y < 0 || pos.y >= 20) {
            return true;
        }
        
        // 檢查蛇身
        if (snake.some(segment => segment.x === pos.x && segment.y === pos.y)) {
            return true;
        }
        
        // 檢查障礙物
        for (let obstacle of obstacles) {
            if (pos.x >= obstacle.x && pos.x < obstacle.x + obstacle.width &&
                pos.y >= obstacle.y && pos.y < obstacle.y + obstacle.height) {
                return true;
            }
        }
        
        return false;
    }
    
    heuristic(a, b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }
    
    posToString(pos) {
        return `${pos.x},${pos.y}`;
    }
    
    reconstructPath(cameFrom, current) {
        const path = [current];
        
        while (cameFrom.has(this.posToString(current))) {
            current = cameFrom.get(this.posToString(current));
            path.unshift(current);
        }
        
        return path;
    }
}

class ParticleSystem {
    constructor() {
        this.particles = [];
    }
    
    addExplosion(x, y, color, count = 15) {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 8,
                vy: (Math.random() - 0.5) * 8,
                life: 60,
                maxLife: 60,
                color: color,
                size: Math.random() * 4 + 2
            });
        }
    }
    
    addTrail(x, y, color) {
        this.particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            life: 30,
            maxLife: 30,
            color: color,
            size: 2
        });
    }
    
    update() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vx *= 0.98; // 阻力
            particle.vy *= 0.98;
            particle.life--;
            
            if (particle.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }
    
    render(ctx) {
        for (let particle of this.particles) {
            const alpha = particle.life / particle.maxLife;
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = particle.color;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size * alpha, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }
}

// 音效管理器
class AudioManager {
    constructor() {
        this.sounds = {};
        this.enabled = true;
        this.volume = 0.5;
    }
    
    loadSound(name, url) {
        const audio = new Audio(url);
        audio.volume = this.volume;
        this.sounds[name] = audio;
    }
    
    play(name) {
        if (this.enabled && this.sounds[name]) {
            this.sounds[name].currentTime = 0;
            this.sounds[name].play().catch(() => {
                // 忽略播放錯誤
            });
        }
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        for (let sound of Object.values(this.sounds)) {
            sound.volume = this.volume;
        }
    }
    
    toggle() {
        this.enabled = !this.enabled;
    }
}

// 導出模組
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        GameEngine,
        AISnakeController,
        AStarPathfinding,
        ParticleSystem,
        AudioManager
    };
}