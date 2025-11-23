/**
 * API Integration for Collaborative Leaderboard
 *
 * This file handles communication with the backend server
 * for fetching and submitting leaderboard scores.
 */

class LeaderboardAPI {
    constructor() {
        this.baseUrl = GameConfig.API_BASE_URL;
        this.localStorageKey = 'special_day_dodger_leaderboard';
    }

    /**
     * Fetch the global leaderboard from the server
     * Falls back to local storage if offline
     */
    async getLeaderboard() {
        try {
            const response = await fetch(`${this.baseUrl}/leaderboard`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch leaderboard');
            }

            const data = await response.json();
            // Cache locally
            this.saveLocal(data);
            return data;
        } catch (error) {
            console.warn('Failed to fetch online leaderboard, using local:', error);
            return this.getLocal();
        }
    }

    /**
     * Submit a new score to the server
     * @param {string} name - Player initials (3 characters)
     * @param {number} score - Tasks avoided count
     */
    async submitScore(name, score) {
        try {
            const response = await fetch(`${this.baseUrl}/score`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    score: score,
                    timestamp: Date.now()
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit score');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.warn('Failed to submit score online, saving locally:', error);
            // Save locally as fallback
            this.addToLocal(name, score);
            return { success: false, message: 'Saved locally' };
        }
    }

    /**
     * Check if a score qualifies for the leaderboard
     * @param {number} score - The score to check
     * @returns {boolean}
     */
    async qualifiesForLeaderboard(score) {
        const leaderboard = await this.getLeaderboard();

        // Always qualify if less than 5 entries
        if (leaderboard.length < 5) {
            return true;
        }

        // Check if score beats the lowest score
        const lowestScore = leaderboard[leaderboard.length - 1].score;
        return score > lowestScore;
    }

    /**
     * Get leaderboard from local storage
     */
    getLocal() {
        try {
            const stored = localStorage.getItem(this.localStorageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Failed to read local leaderboard:', error);
            return [];
        }
    }

    /**
     * Save leaderboard to local storage
     */
    saveLocal(data) {
        try {
            localStorage.setItem(this.localStorageKey, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save local leaderboard:', error);
        }
    }

    /**
     * Add a score to local storage
     */
    addToLocal(name, score) {
        const leaderboard = this.getLocal();
        leaderboard.push({ name, score });
        leaderboard.sort((a, b) => b.score - a.score);
        leaderboard.splice(5); // Keep top 5
        this.saveLocal(leaderboard);
    }
}

// Export singleton instance
const leaderboardAPI = new LeaderboardAPI();
