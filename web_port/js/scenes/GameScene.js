/**
 * Game Scene - Main gameplay
 */
class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }

    create() {
        this.setupGameState();
        this.createBackground();
        this.createPlayer();
        this.createObstacleGroup();
        this.setupInput();
        this.setupTouchControls();
        this.createUI();
        this.setupAudio();
    }

    setupGameState() {
        const cfg = GameConfig;

        // Game state
        this.tasksAvoided = 0;
        this.obstacleSpeed = cfg.INITIAL_OBSTACLE_SPEED;
        this.spawnRate = cfg.INITIAL_SPAWN_RATE;

        // Special event timing
        this.specialEventTimer = this.time.now;
        this.specialEventInterval = Phaser.Math.Between(
            cfg.SPECIAL_EVENT_MIN * 1000,
            cfg.SPECIAL_EVENT_MAX * 1000
        );
        this.maddieDisplayTime = -10000;
        this.boostEndTime = -10000;

        // Laser state
        this.laser = null;
        this.laserTrail = [];

        // Touch controls
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.isTouching = false;
    }

    createBackground() {
        this.add.image(
            GameConfig.SCREEN_WIDTH / 2,
            GameConfig.SCREEN_HEIGHT / 2,
            'dodgebg'
        ).setDisplaySize(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT);
    }

    createPlayer() {
        const cfg = GameConfig;

        this.player = this.physics.add.sprite(
            cfg.PLAYER_START_X,
            cfg.SCREEN_HEIGHT / 2,
            'andreas'
        );

        this.player.setDisplaySize(cfg.PLAYER_SIZE, cfg.PLAYER_SIZE);
        this.player.setCollideWorldBounds(false); // We handle wrapping manually
        this.player.body.setSize(
            cfg.PLAYER_SIZE * (1 - 2 * cfg.COLLISION_BUFFER),
            cfg.PLAYER_SIZE * (1 - 2 * cfg.COLLISION_BUFFER)
        );
        this.player.body.setOffset(
            cfg.PLAYER_SIZE * cfg.COLLISION_BUFFER,
            cfg.PLAYER_SIZE * cfg.COLLISION_BUFFER
        );
    }

    createObstacleGroup() {
        this.obstacles = this.physics.add.group();
    }

    setupInput() {
        // Keyboard controls
        this.cursors = this.input.keyboard.createCursorKeys();
        this.wasd = this.input.keyboard.addKeys({
            up: Phaser.Input.Keyboard.KeyCodes.W,
            down: Phaser.Input.Keyboard.KeyCodes.S,
            left: Phaser.Input.Keyboard.KeyCodes.A,
            right: Phaser.Input.Keyboard.KeyCodes.D
        });

        this.spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
        this.mKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.M);
    }

    setupTouchControls() {
        // Touch/pointer events
        this.input.on('pointerdown', (pointer) => {
            this.isTouching = true;
            this.touchStartX = pointer.x;
            this.touchStartY = pointer.y;
        });

        this.input.on('pointermove', (pointer) => {
            if (this.isTouching) {
                this.handleTouchMove(pointer);
            }
        });

        this.input.on('pointerup', () => {
            this.isTouching = false;
        });

        // Tap to shoot
        this.input.on('pointerdown', (pointer) => {
            // If tap is brief and not dragging, shoot laser
            if (!this.laser) {
                this.time.delayedCall(100, () => {
                    if (!this.isTouching) {
                        this.shootLaser();
                    }
                });
            }
        });
    }

    handleTouchMove(pointer) {
        const cfg = GameConfig;
        const deltaX = pointer.x - this.touchStartX;
        const deltaY = pointer.y - this.touchStartY;

        // Update player position based on drag
        const sensitivity = 0.5; // Adjust for smoother/faster movement
        this.player.x += deltaX * sensitivity;
        this.player.y += deltaY * sensitivity;

        // Update touch start position
        this.touchStartX = pointer.x;
        this.touchStartY = pointer.y;

        // Clamp horizontal movement
        if (this.player.x < 0) this.player.x = 0;
        if (this.player.x > cfg.SCREEN_WIDTH - cfg.PLAYER_SIZE) {
            this.player.x = cfg.SCREEN_WIDTH - cfg.PLAYER_SIZE;
        }

        // Handle vertical wrapping
        this.handleVerticalWrap();
    }

    createUI() {
        this.scoreText = this.add.text(20, 20, 'Tasks avoided: 0', {
            fontSize: '24px',
            fill: '#000000',
            fontFamily: 'Arial',
            stroke: '#ffffff',
            strokeThickness: 2
        });

        // Maddie villain sprite (hidden initially)
        this.maddieSprite = this.add.image(
            GameConfig.SCREEN_WIDTH - 110,
            GameConfig.SCREEN_HEIGHT / 2,
            'maddievillain'
        );
        this.maddieSprite.setDisplaySize(200, 200);
        this.maddieSprite.setVisible(false);

        // Maddie text
        this.maddieText = this.add.text(
            GameConfig.SCREEN_WIDTH - 270,
            200,
            "IT'S MY\nSPECIAL\nDAY!!!",
            {
                fontSize: '24px',
                fill: '#000000',
                fontFamily: 'Arial',
                lineSpacing: 5
            }
        );
        this.maddieText.setVisible(false);
    }

    setupAudio() {
        this.pewSound = this.sound.add('pew', { volume: 0.5 });
        this.specialDaySound = this.sound.add('specialDay', { volume: 1.0 });
        this.loseSound = this.sound.add('loseSound', { volume: 0.7 });
    }

    update(time, delta) {
        this.handleKeyboardInput();
        this.handleMuteToggle();
        this.updateLaser();
        this.spawnObstacles();
        this.updateObstacles();
        this.checkCollisions();
        this.handleSpecialEvent(time);
        this.updateMaddieDisplay(time);
        this.updateScore();
    }

    handleKeyboardInput() {
        const speed = 5;
        const cfg = GameConfig;

        // Horizontal movement
        if (this.cursors.left.isDown || this.wasd.left.isDown) {
            this.player.x -= speed;
            if (this.player.x < 0) this.player.x = 0;
        }
        if (this.cursors.right.isDown || this.wasd.right.isDown) {
            this.player.x += speed;
            if (this.player.x > cfg.SCREEN_WIDTH - cfg.PLAYER_SIZE) {
                this.player.x = cfg.SCREEN_WIDTH - cfg.PLAYER_SIZE;
            }
        }

        // Vertical movement
        if (this.cursors.up.isDown || this.wasd.up.isDown) {
            this.player.y -= speed;
        }
        if (this.cursors.down.isDown || this.wasd.down.isDown) {
            this.player.y += speed;
        }

        // Handle vertical wrapping
        this.handleVerticalWrap();

        // Shooting
        if (Phaser.Input.Keyboard.JustDown(this.spaceKey)) {
            this.shootLaser();
        }
    }

    handleVerticalWrap() {
        const cfg = GameConfig;
        const wrapThreshold = cfg.PLAYER_SIZE * cfg.WRAP_THRESHOLD;

        if (this.player.y + wrapThreshold > cfg.SCREEN_HEIGHT) {
            this.player.y = -wrapThreshold;
        } else if (this.player.y < -wrapThreshold) {
            this.player.y = cfg.SCREEN_HEIGHT - wrapThreshold;
        }
    }

    handleMuteToggle() {
        if (Phaser.Input.Keyboard.JustDown(this.mKey)) {
            const muted = !this.registry.get('muted');
            this.registry.set('muted', muted);
            this.sound.mute = muted;
        }
    }

    shootLaser() {
        if (this.laser) return;

        const cfg = GameConfig;

        this.laser = this.add.rectangle(
            this.player.x + cfg.PLAYER_SIZE / 2,
            this.player.y + cfg.PLAYER_SIZE / 2,
            cfg.LASER_SIZE.width,
            cfg.LASER_SIZE.height,
            cfg.COLORS.RED
        );

        this.laserTrail = [];

        if (!this.registry.get('muted')) {
            this.pewSound.play();
        }
    }

    updateLaser() {
        if (!this.laser) return;

        const cfg = GameConfig;

        // Add to trail
        this.laserTrail.push({ x: this.laser.x, y: this.laser.y });
        if (this.laserTrail.length > 10) {
            this.laserTrail.shift();
        }

        // Move laser
        this.laser.x += cfg.LASER_SPEED;

        // Remove if off-screen
        if (this.laser.x > cfg.SCREEN_WIDTH) {
            this.laser.destroy();
            this.laser = null;
            this.laserTrail = [];
        }
    }

    spawnObstacles() {
        if (Math.random() < this.spawnRate / 60) { // Adjust for frame rate
            this.spawnObstacle();
        }
    }

    spawnObstacle() {
        const cfg = GameConfig;

        // Pick random obstacle type (excluding maddievillain)
        const types = Object.keys(cfg.OBJECT_SIZES).filter(t => t !== 'maddievillain');
        const type = Phaser.Utils.Array.GetRandom(types);
        const size = cfg.OBJECT_SIZES[type];

        const obstacle = this.obstacles.create(
            cfg.SCREEN_WIDTH,
            Phaser.Math.Between(0, cfg.SCREEN_HEIGHT - size),
            type
        );

        obstacle.setDisplaySize(size, size);
        obstacle.setVelocityX(-this.obstacleSpeed * 60); // Convert to pixels per second
        obstacle.body.setSize(
            size * (1 - 2 * cfg.COLLISION_BUFFER),
            size * (1 - 2 * cfg.COLLISION_BUFFER)
        );
        obstacle.body.setOffset(
            size * cfg.COLLISION_BUFFER,
            size * cfg.COLLISION_BUFFER
        );
        obstacle.obstacleSize = size;
    }

    updateObstacles() {
        const cfg = GameConfig;

        // Remove off-screen obstacles and count avoided
        this.obstacles.children.entries.forEach(obstacle => {
            if (obstacle.x + obstacle.obstacleSize < 0) {
                this.tasksAvoided++;
                obstacle.destroy();
            }
        });

        // Gradually increase difficulty
        this.obstacleSpeed += cfg.SPEED_INCREMENT / cfg.FPS;
    }

    checkCollisions() {
        const cfg = GameConfig;

        // Check player-obstacle collision
        this.obstacles.children.entries.forEach(obstacle => {
            if (this.checkOverlap(this.player, obstacle)) {
                this.gameOver();
            }

            // Check laser-obstacle collision
            if (this.laser && this.checkLaserHit(obstacle)) {
                this.tasksAvoided++;
                obstacle.destroy();
                this.laser.destroy();
                this.laser = null;
                this.laserTrail = [];
            }
        });
    }

    checkOverlap(sprite1, sprite2) {
        const bounds1 = sprite1.getBounds();
        const bounds2 = sprite2.getBounds();

        return Phaser.Geom.Intersects.RectangleToRectangle(bounds1, bounds2);
    }

    checkLaserHit(obstacle) {
        if (!this.laser) return false;

        const cfg = GameConfig;
        const laserBounds = this.laser.getBounds();
        const obstacleBounds = obstacle.getBounds();

        return Phaser.Geom.Intersects.RectangleToRectangle(laserBounds, obstacleBounds);
    }

    handleSpecialEvent(time) {
        const cfg = GameConfig;
        const elapsed = time - this.specialEventTimer;

        // Increase difficulty during special event buildup
        if (elapsed > 15000 && elapsed < 45000) {
            this.spawnRate = Math.min(this.spawnRate + 0.001 / 60, 0.12);
            this.obstacleSpeed = Math.min(this.obstacleSpeed + 0.01 / 60, 4);
        }

        // Trigger special event
        if (elapsed > this.specialEventInterval) {
            this.triggerSpecialEvent(time);
        }

        // End boost period
        if (time > this.boostEndTime) {
            this.spawnRate = cfg.INITIAL_SPAWN_RATE;
        }
    }

    triggerSpecialEvent(time) {
        const cfg = GameConfig;

        this.maddieDisplayTime = time;
        this.boostEndTime = time + cfg.SPECIAL_EVENT_BOOST_TIME * 1000;
        this.spawnRate = Math.min(0.1, 0.06);

        if (!this.registry.get('muted')) {
            this.specialDaySound.play();
        }

        this.specialEventTimer = time;
        this.specialEventInterval = Phaser.Math.Between(
            cfg.SPECIAL_EVENT_MIN * 1000,
            cfg.SPECIAL_EVENT_MAX * 1000
        );
    }

    updateMaddieDisplay(time) {
        const cfg = GameConfig;
        const elapsed = time - this.maddieDisplayTime;
        const isVisible = elapsed < cfg.SPECIAL_EVENT_DISPLAY_TIME * 1000;

        this.maddieSprite.setVisible(isVisible);
        this.maddieText.setVisible(isVisible);
    }

    updateScore() {
        this.scoreText.setText(`Tasks avoided: ${this.tasksAvoided}`);
    }

    gameOver() {
        // Stop music
        this.sound.stopAll();

        // Play lose sound
        if (!this.registry.get('muted')) {
            this.loseSound.play();
        }

        // Store score and transition
        this.registry.set('finalScore', this.tasksAvoided);
        this.scene.start('GameOverScene');
    }
}
