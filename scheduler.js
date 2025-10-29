import cron from 'node-cron';
import { exec } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// ES modules don't have __dirname so we recreate it
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const pythonScript = join(__dirname, 'news_fetcher.py');

function runNewsScript() {
    console.log(`[${new Date().toLocaleString()}] Starting news fetch...`);
    
    exec(`python3 ${pythonScript}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return;
        }
        console.log(stdout);
    });
}

// Schedule to run every 24 hours at 2:00 AM CDT
cron.schedule('0 2 * * *', () => {
    runNewsScript();
}, {
    scheduled: true,
    timezone: "America/Chicago"
});

console.log('📅 News scheduler is running...');
console.log('⏰ Will fetch news every 24 hours at 2:00 AM CDT');
console.log('Press Ctrl+C to stop\n');

// Run on startup as well
runNewsScript();
