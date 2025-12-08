const puppeteer = require('puppeteer');

const targetUrl = process.argv[2];

if (!targetUrl) {
    console.error("Usage: node bot.js <url>");
    process.exit(1);
}

(async () => {
    try {
        const browser = await puppeteer.launch({
            // Ensure we use the installed Chrome
            executablePath: '/usr/bin/chromium',
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        });

        const page = await browser.newPage();

        // Parse the domain to set the cookie correctly
        const urlObj = new URL(targetUrl);

        // Set the flag cookie
        await page.setCookie({
            name: 'flag',
            value: 'BCT{4_h34r7_m4d3_full_m374l}',
            domain: urlObj.hostname, 
            path: '/',
            httpOnly: false,
            secure: false
        });

        console.log(`[*] Visiting ${targetUrl}`);

        try {
            // Visit the page
            // We change 'waitUntil' to 'domcontentloaded' so it doesn't wait for network silence
            await page.goto(targetUrl, {
                waitUntil: 'domcontentloaded',
                timeout: 5000
            });
        } catch (err) {
            // IGNORE THE "FRAME DETACHED" ERROR
            // If the XSS works, the frame WILL detach (redirect). This is expected.
            console.log(`[INFO] Navigation happened (XSS triggered?): ${err.message}`);
        }

        console.log("[*] waiting for XSS execution...");
        
        // CRITICAL: Keep browser open for 5 seconds to let the redirect request finish
        await new Promise(resolve => setTimeout(resolve, 5000));

        await browser.close();
        console.log("[*] Visit complete.");

    } catch (error) {
        console.error(`[!] Fatal Error: ${error.message}`);
        process.exit(1);
    }
})();
