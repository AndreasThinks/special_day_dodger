/**
 * Game Over Scene - Score submission and leaderboard
 */
class GameOverScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameOverScene' });
        this.currentInitial = 0;
        this.initials = ['A', 'A', 'A'];
        this.isEnteringInitials = false;
    }

    create() {
        this.score = this.registry.get('finalScore') || 0;
        this.createBackground();
        this.showGameOverMessage();
    }

    createBackground() {
        const { SCREEN_WIDTH, SCREEN_HEIGHT } = GameConfig;

        // Black background
        this.add.rectangle(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            0x000000
        );
    }

    async showGameOverMessage() {
        const { SCREEN_WIDTH, SCREEN_HEIGHT } = GameConfig;

        // Game over text
        this.add.text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 40,
            'Oops. Responsibility caught up with Andreas.',
            {
                fontSize: '24px',
                fill: '#ffffff',
                fontFamily: 'Arial',
                align: 'center'
            }
        ).setOrigin(0.5);

        // Wait a bit before checking leaderboard
        await this.delay(2000);

        // Check if score qualifies for leaderboard
        const qualifies = await leaderboardAPI.qualifiesForLeaderboard(this.score);

        if (qualifies) {
            this.enterInitials();
        } else {
            this.showLeaderboard();
        }
    }

    enterInitials() {
        this.isEnteringInitials = true;

        const { SCREEN_WIDTH, SCREEN_HEIGHT } = GameConfig;

        // Clear screen
        this.children.removeAll();
        this.createBackground();

        // Title
        this.add.text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 100,
            'Enter Your Initials:',
            {
                fontSize: '24px',
                fill: '#ffffff',
                fontFamily: 'Arial'
            }
        ).setOrigin(0.5);

        // Create initial displays
        this.initialTexts = [];
        const spacing = 80;
        const startX = SCREEN_WIDTH / 2 - spacing;

        for (let i = 0; i < 3; i++) {
            const text = this.add.text(
                startX + i * spacing,
                SCREEN_HEIGHT / 2,
                this.initials[i],
                {
                    fontSize: '50px',
                    fill: '#ffffff',
                    fontFamily: 'Arial',
                    stroke: '#000000',
                    strokeThickness: 4
                }
            ).setOrigin(0.5);
            this.initialTexts.push(text);
        }

        // Highlight current letter
        this.updateHighlight();

        // Instructions
        this.add.text(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 80,
            'Use Arrow Keys or Tap +/- to change letter\nPress ENTER or TAP when done',
            {
                fontSize: '18px',
                fill: '#cccccc',
                fontFamily: 'Arial',
                align: 'center'
            }
        ).setOrigin(0.5);

        // Mobile controls
        this.createMobileControls();

        // Keyboard input
        this.input.keyboard.on('keydown', this.handleInitialInput, this);
    }

    createMobileControls() {
        const { SCREEN_WIDTH, SCREEN_HEIGHT } = GameConfig;

        // Up/Down buttons for current letter
        const buttonStyle = {
            fontSize: '30px',
            fill: '#ffffff',
            backgroundColor: '#333333',
            padding: { x: 20, y: 10 }
        };

        // Up button
        this.upButton = this.add.text(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 150, '▲', buttonStyle)
            .setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => this.changeCurrentLetter(1));

        // Down button
        this.downButton = this.add.text(SCREEN_WIDTH / 2 + 100, SCREEN_HEIGHT / 2 + 150, '▼', buttonStyle)
            .setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => this.changeCurrentLetter(-1));

        // Next button
        this.nextButton = this.add.text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 200, 'Next >', buttonStyle)
            .setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => this.nextInitial());

        // Done button (hidden until last initial)
        this.doneButton = this.add.text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 200, 'Done ✓', {
            ...buttonStyle,
            fill: '#00ff00'
        })
            .setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => this.submitInitials())
            .setVisible(false);
    }

    handleInitialInput(event) {
        if (!this.isEnteringInitials) return;

        if (event.key === 'ArrowUp') {
            this.changeCurrentLetter(1);
        } else if (event.key === 'ArrowDown') {
            this.changeCurrentLetter(-1);
        } else if (event.key === 'ArrowRight' || event.key === 'Enter') {
            this.nextInitial();
        } else if (event.key === 'ArrowLeft' && this.currentInitial > 0) {
            this.currentInitial--;
            this.updateHighlight();
        } else if (event.key.length === 1 && /[A-Z]/i.test(event.key)) {
            this.initials[this.currentInitial] = event.key.toUpperCase();
            this.updateInitialDisplay();
            this.nextInitial();
        }
    }

    changeCurrentLetter(direction) {
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const currentIndex = alphabet.indexOf(this.initials[this.currentInitial]);
        let newIndex = (currentIndex + direction + alphabet.length) % alphabet.length;
        this.initials[this.currentInitial] = alphabet[newIndex];
        this.updateInitialDisplay();
    }

    nextInitial() {
        if (this.currentInitial < 2) {
            this.currentInitial++;
            this.updateHighlight();
        } else {
            this.submitInitials();
        }
    }

    updateInitialDisplay() {
        for (let i = 0; i < 3; i++) {
            this.initialTexts[i].setText(this.initials[i]);
        }
    }

    updateHighlight() {
        for (let i = 0; i < 3; i++) {
            if (i === this.currentInitial) {
                this.initialTexts[i].setFill('#ffff00');
                this.initialTexts[i].setScale(1.2);
            } else {
                this.initialTexts[i].setFill('#ffffff');
                this.initialTexts[i].setScale(1.0);
            }
        }

        // Show/hide done button on last initial
        if (this.nextButton && this.doneButton) {
            this.nextButton.setVisible(this.currentInitial < 2);
            this.doneButton.setVisible(this.currentInitial === 2);
        }
    }

    async submitInitials() {
        this.isEnteringInitials = false;
        this.input.keyboard.off('keydown', this.handleInitialInput, this);

        const name = this.initials.join('');

        // Show submitting message
        this.children.removeAll();
        this.createBackground();

        this.add.text(
            GameConfig.SCREEN_WIDTH / 2,
            GameConfig.SCREEN_HEIGHT / 2,
            'Submitting score...',
            {
                fontSize: '24px',
                fill: '#ffffff',
                fontFamily: 'Arial'
            }
        ).setOrigin(0.5);

        // Submit to API
        await leaderboardAPI.submitScore(name, this.score);

        // Show leaderboard
        this.showLeaderboard();
    }

    async showLeaderboard() {
        // Clear screen
        this.children.removeAll();
        this.createBackground();

        const { SCREEN_WIDTH, SCREEN_HEIGHT } = GameConfig;

        // Title
        this.add.text(
            SCREEN_WIDTH / 2,
            80,
            'LEADERBOARD - MOST AVOIDANT LEGENDS',
            {
                fontSize: '24px',
                fill: '#ffffff',
                fontFamily: 'Arial',
                stroke: '#000000',
                strokeThickness: 3
            }
        ).setOrigin(0.5);

        // Fetch leaderboard
        const leaderboard = await leaderboardAPI.getLeaderboard();

        // Display leaderboard
        const startY = 150;
        const spacing = 50;

        if (leaderboard.length === 0) {
            this.add.text(
                SCREEN_WIDTH / 2,
                startY + 100,
                'No scores yet. Be the first!',
                {
                    fontSize: '24px',
                    fill: '#cccccc',
                    fontFamily: 'Arial'
                }
            ).setOrigin(0.5);
        } else {
            leaderboard.forEach((entry, index) => {
                const text = `${index + 1}. ${entry.name} - ${entry.score}`;
                const color = index === 0 ? '#FFD700' : '#ffffff'; // Gold for first place

                this.add.text(
                    SCREEN_WIDTH / 2,
                    startY + index * spacing,
                    text,
                    {
                        fontSize: '36px',
                        fill: color,
                        fontFamily: 'Arial',
                        stroke: '#000000',
                        strokeThickness: 2
                    }
                ).setOrigin(0.5);
            });
        }

        // Instructions
        const instructionY = Math.max(startY + leaderboard.length * spacing + 50, 450);

        this.add.text(
            SCREEN_WIDTH / 2,
            instructionY,
            'Press ENTER or TAP to Restart',
            {
                fontSize: '20px',
                fill: '#cccccc',
                fontFamily: 'Arial'
            }
        ).setOrigin(0.5);

        // Input to restart
        this.input.keyboard.once('keydown-ENTER', () => this.restart());
        this.input.once('pointerdown', () => this.restart());
    }

    restart() {
        // Restart background music
        const bgMusic = this.sound.get('bgMusic');
        if (bgMusic && !bgMusic.isPlaying) {
            bgMusic.play();
        }

        this.scene.start('StartScene');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
