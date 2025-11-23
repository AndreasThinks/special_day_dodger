// Game configuration constants
const GameConfig = {
    // Display
    SCREEN_WIDTH: 800,
    SCREEN_HEIGHT: 600,

    // Player
    PLAYER_SIZE: 100,
    PLAYER_START_X: 10,

    // Laser
    LASER_SIZE: { width: 5, height: 5 },
    LASER_SPEED: 7,

    // Obstacles
    SPEED_INCREMENT: 0.005,
    INITIAL_OBSTACLE_SPEED: 2,
    INITIAL_SPAWN_RATE: 0.02,

    // Game
    FPS: 60,

    // Colors
    COLORS: {
        WHITE: 0xFFFFFF,
        BLACK: 0x000000,
        RED: 0xFF0000,
        LIGHT_GREEN: 0x90EE90
    },

    // Object sizes
    OBJECT_SIZES: {
        'flowers': 100,
        'spreadsheet': 50,
        'invitation': 60,
        'rings': 40,
        'tux': 100,
        'list': 50,
        'maddievillain': 200
    },

    // Special events
    SPECIAL_EVENT_MIN: 20,
    SPECIAL_EVENT_MAX: 30,
    SPECIAL_EVENT_DISPLAY_TIME: 5,
    SPECIAL_EVENT_BOOST_TIME: 10,

    // Collision buffer (20% padding)
    COLLISION_BUFFER: 0.2,

    // Wrap threshold (35% of player size)
    WRAP_THRESHOLD: 0.35,

    // API endpoint (update this to your backend URL)
    API_BASE_URL: '/api'  // Change to 'https://yourbackend.com/api' in production
};
