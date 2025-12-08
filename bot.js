const puppeteer = require('puppeteer');

const targetUrl = process.argv[2];

if (!targetUrl) {
    console.error("Usage: node bot.js <url>");
    process.exit(1);
}

(async () => {
    try {
        const browser = await puppeteer.launch({
            executablePath: '/usr/bin/chromium',
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        });

        const page = await browser.newPage();

        const urlObj = new URL(targetUrl);

        await page.setCookie({
            name: 'flag',
            value: 'BCT{4_h34r7_m4d3_full_m374l}',
            domain: urlObj.hostname,
            path: '/',
            httpOnly: false, // Must be false so XSS can read it (document.cookie)
            secure: false
        });

        console.log(`[*] Visiting ${targetUrl}`);

        // Visit the page
        await page.goto(targetUrl, {
            waitUntil: 'networkidle2',
            timeout: 5000
        });

        // Wait a bit for any XSS to trigger
        await new Promise(resolve => setTimeout(resolve, 2000));

        await browser.close();
        console.log("[*] Visit complete.");

    } catch (error) {
        console.error(`[!] Error: ${error.message}`);
        process.exit(1);
    }
})();
