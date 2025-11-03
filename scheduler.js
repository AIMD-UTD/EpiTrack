import { Cron } from 'croner';
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

// Schedule to run every 24 hours using Croner
// Croner runs continuously even when terminal is closed if running as a service
const job = new Cron('0 2 * * *', {
    timezone: 'America/Chicago',
    startAt: new Date(), // Start immediately
    catch: true, // Catch errors and continue
    onTrigger: () => {
        console.log(`[${new Date().toLocaleString()}] Scheduled job triggered`);
        runNewsScript();
    }
});

console.log('📅 News scheduler is running with Croner...');
console.log('⏰ Will fetch news every 24 hours at 2:00 AM CDT');
console.log(`⏰ Next run scheduled for: ${job.nextRun()}`);
console.log('Press Ctrl+C to stop\n');

// Run on startup as well
runNewsScript();

// Keep the process alive
process.on('SIGINT', () => {
    console.log('\n📅 Stopping scheduler...');
    job.stop();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n📅 Stopping scheduler...');
    job.stop();
    process.exit(0);
});
