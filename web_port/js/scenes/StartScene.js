/**
 * Start Scene - Title screen and instructions
 */
class StartScene extends Phaser.Scene {
    constructor() {
        super({ key: 'StartScene' });
    }

    preload() {
        // Show loading progress
        this.createLoadingBar();

        // Set asset paths
        const basePath = 'assets/';

        // Load images
        this.load.image('andreas', basePath + 'images/andreas.png');
        this.load.image('dodgebg', basePath + 'images/dodgebg.png');
        this.load.image('flowers', basePath + 'images/flowers.png');
        this.load.image('spreadsheet', basePath + 'images/spreadsheet.png');
        this.load.image('invitation', basePath + 'images/invitation.png');
        this.load.image('rings', basePath + 'images/rings.png');
        this.load.image('tux', basePath + 'images/tux.png');
        this.load.image('list', basePath + 'images/list.png');
        this.load.image('maddievillain', basePath + 'images/maddievillain.png');

        // Load audio
        this.load.audio('bgMusic', basePath + 'audio/happy_whistle_tune.mp3');
        this.load.audio('pew', basePath + 'audio/pew.mp3');
        this.load.audio('specialDay', basePath + 'audio/special_day.mp3');
        this.load.audio('loseSound', basePath + 'audio/lose_sound.mp3');
    }

    createLoadingBar() {
        const width = GameConfig.SCREEN_WIDTH;
        const height = GameConfig.SCREEN_HEIGHT;

        const progressBar = this.add.graphics();
        const progressBox = this.add.graphics();
        progressBox.fillStyle(0x222222, 0.8);
        progressBox.fillRect(width / 4, height / 2 - 30, width / 2, 50);

        const loadingText = this.make.text({
            x: width / 2,
            y: height / 2 - 50,
            text: 'Loading...',
            style: {
                font: '20px Arial',
                fill: '#ffffff'
            }
        });
        loadingText.setOrigin(0.5, 0.5);

        this.load.on('progress', (value) => {
            progressBar.clear();
            progressBar.fillStyle(0xffffff, 1);
            progressBar.fillRect(width / 4 + 10, height / 2 - 20, (width / 2 - 20) * value, 30);
        });

        this.load.on('complete', () => {
            progressBar.destroy();
            progressBox.destroy();
            loadingText.destroy();
        });
    }

    create() {
        const { SCREEN_WIDTH, SCREEN_HEIGHT } = GameConfig;

        // Hide loading screen
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }

        // Background
        this.add.image(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 'dodgebg')
            .setDisplaySize(SCREEN_WIDTH, SCREEN_HEIGHT);

        // Semi-transparent overlay
        const overlay = this.add.rectangle(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            0x000000,
            0.6
        );

        // Title
        const titleStyle = {
            fontSize: '72px',
            fill: '#ffffff',
            fontFamily: 'Arial, sans-serif',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 6,
            shadow: {
                offsetX: 3,
                offsetY: 3,
                color: '#000000',
                blur: 5,
                fill: true
            }
        };

        this.add.text(SCREEN_WIDTH / 2, 150, 'Special Day Dodger', titleStyle)
            .setOrigin(0.5);

        // Instructions
        const instructionStyle = {
            fontSize: '24px',
            fill: '#ffffff',
            fontFamily: 'Arial',
            align: 'center',
            lineSpacing: 10
        };

        const instructions = [
            'Help Andreas avoid his wedding responsibilities.',
            '',
            'Desktop: Arrow keys or WASD to move',
            'Mobile: Touch and drag to move',
            'Space or Tap to shoot',
            '',
            'Press ENTER or TAP to Start'
        ];

        this.add.text(SCREEN_WIDTH / 2, 300, instructions.join('\n'), instructionStyle)
            .setOrigin(0.5);

        // Mute instruction
        this.muteText = this.add.text(SCREEN_WIDTH / 2, 520, 'Press M to Mute', {
            fontSize: '18px',
            fill: '#cccccc',
            fontFamily: 'Arial'
        }).setOrigin(0.5);

        // Start music
        if (!this.sound.get('bgMusic')) {
            this.bgMusic = this.sound.add('bgMusic', {
                loop: true,
                volume: 0.2
            });
            this.bgMusic.play();
        }

        // Input handlers
        this.input.keyboard.on('keydown-ENTER', () => this.startGame());
        this.input.keyboard.on('keydown-M', () => this.toggleMute());

        // Touch/click to start
        this.input.on('pointerdown', () => this.startGame());

        // Store mute state globally
        if (this.registry.get('muted') === undefined) {
            this.registry.set('muted', false);
        }
    }

    startGame() {
        this.scene.start('GameScene');
    }

    toggleMute() {
        const muted = !this.registry.get('muted');
        this.registry.set('muted', muted);
        this.sound.mute = muted;

        this.muteText.setText(muted ? 'Sound: OFF (Press M)' : 'Press M to Mute');
    }
}
