const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const url = process.argv[2];
const timeout = 5000;

console.log('Gemini: Trying to access to web-page.');

(async () => {
    console.log("Accessed!");
    const browser = await puppeteer.launch( {
        headless: "false",
        args: ['--no-sandbox'],
    } );
    
    const page = await browser.newPage();

    await page.setViewport( {
        width: 1200,
        height: 1200,
        deviceScaleFactor: 1,
    } );

    await page.goto( url, {
        waitUntil: "domcontentloaded",
        timeout: timeout,
    } );

    await new Promise(resolve => setTimeout(resolve, timeout));

    await page.screenshot({
        path: "screenshot.jpg",
        fullPage: true,
    });

    await browser.close();
})();