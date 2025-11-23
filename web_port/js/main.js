/**
 * Main game initialization
 */

// Phaser game configuration
const config = {
    type: Phaser.AUTO,
    width: GameConfig.SCREEN_WIDTH,
    height: GameConfig.SCREEN_HEIGHT,
    parent: 'game-container',
    backgroundColor: '#000000',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 },
            debug: false
        }
    },
    scene: [StartScene, GameScene, GameOverScene],
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        width: GameConfig.SCREEN_WIDTH,
        height: GameConfig.SCREEN_HEIGHT
    },
    audio: {
        disableWebAudio: false
    }
};

// Create game instance
const game = new Phaser.Game(config);

// Handle window resize for responsive behavior
window.addEventListener('resize', () => {
    game.scale.refresh();
});

// Prevent default touch behaviors on mobile
document.addEventListener('touchmove', (e) => {
    e.preventDefault();
}, { passive: false });

// Disable context menu on long press
document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});
