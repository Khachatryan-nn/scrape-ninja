const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const { GoogleGenerativeAI } = require("@google/generative-ai");
const { HarmBlockThreshold, HarmCategory } = require("@google/generative-ai");
const readline = require('readline');
const fs = require('fs');
require('dotenv').config();

puppeteer.use(StealthPlugin());

const genAI = new GoogleGenerativeAI(process.env.API_KEY_1);
const SLEEP_TIME = process.env.SLEEP_TIME || 5000;
const urlRegex = /"url":\s*"([^"]+)"/;
const { stdin, stdout } = process;
const timeout = 5000;


// // console.log(process.env.API_KEY_1)
model_name = "gemini-1.5-pro-latest";

// Safety settings for GenAI
const safetySettings = [
	{
		category: HarmCategory.HARM_CATEGORY_HARASSMENT,
		threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH,
	},
	{
		category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,
		threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH,
	},
	{
		"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
		"threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH,
	},
	{
		"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
		"threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH,
	}
];

// PROMPT TEMPLATE
const prompt_template = `You are a website crawler. You will be given instructions on what to do by browsing. You are connected to a web browser and you will be given the screenshot of the website you are on. The links on the website will be highlighted in red in the screenshot. Always read what is in the screenshot. Don't guess link names.
			
You can go to a specific URL by answering with the following JSON format:
{"url": "url goes here"}

You can click links on the website by referencing the text inside of the link/button, by answering in the following JSON format:
{"click": "Text in link"}

Once you are on a URL and you have found the answer to the user's question, you can answer with a regular message.

Use google search by set a sub-page like 'https://google.com/search?q=search' if applicable. Prefer to use Google. Only if the user provides a direct URL, go to that one. Do not make up links.

If you asked for cookies, or there are any other pop-ups, close with cross or accept them to load the website.
If you cannot naviagte through website, try to search in Google.`

const click_prompt_template = `Here's the screenshot of the website you are on right now. You can click on links (marked in red rectangles in the screenshot) with the following format:{\"click\": \"Link text\"} or you can crawl to another URL if this one is incorrect.
If you asked for cookies, accept them to load the website.
If you find the answer to the user's question, respond strictly with the requested information, surely formatted in the JSON format.
Do not provide any additional comments or information.`
//END THERE

function image_to_base64(path, mimeType) {
	return {
	  inlineData: {
		data: Buffer.from(fs.readFileSync(path)).toString("base64"),
		mimeType
	  },
	};
}

async function input( text ) {
    let the_prompt;

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    await (async () => {
        return new Promise( resolve => {
            rl.question( text, (prompt) => {
                the_prompt = prompt;
                rl.close();
                resolve();
            } );
        } );
    })();

    return the_prompt;
}

// Function to send message to python stdin
function sendMessageToPython(message) {
    const pythonProcess = spawn('python', ['main.py']);
    pythonProcess.stdin.write(message);
    pythonProcess.stdin.end();
}

// Function to receive message from Python stdout
function receiveMessageFromPython() {
    return new Promise(resolve => {
        const pythonProcess = spawn('python', ['main.py']);
        let output = '';
        pythonProcess.stdout.on('data', data => {
            output += data.toString().trim();
        });
        pythonProcess.on('close', () => {
            resolve(output);
        });
    });
}

async function sleep( milliseconds ) {
    return await new Promise((r, _) => {
        setTimeout( () => {
            r();
        }, milliseconds );
    });
}

async function highlight_links( page ) {
	console.error('Highlighting links...')
	await sleep(1000);
    try {
        await page.evaluate(() => {
            document.querySelectorAll('[gemini-link-text]').forEach(e => {
                if (e) {
                    e.removeAttribute("gemini-link-text");
                }
            });
        });
    } catch (e) {
        console.error("highlight_links: Exception while removing old links: " + e);
    }

    try {
		const clickableSelectors = [
            'a',
            'button',
            '[role=button]',
            'input',
            'textarea',
            '[role=treeitem]',
            '[onclick]'
        ];

        const elements = await page.$$((clickableSelectors.join(',')));

        elements.forEach( async e => {
            try {
                await page.evaluate(e => {
                    function isElementVisible(el) {
                        if (!el) {
                            throw new Error("Element does not exist");
                        }

                        function isStyleVisible(el) {
                            const style = window.getComputedStyle(el);
                            if (!style) {
                                throw new Error("Computed style is null");
                            }
                            return style.width !== '0' &&
                                   style.height !== '0' &&
                                   style.opacity !== '0' &&
                                   style.display !== 'none' &&
                                   style.visibility !== 'hidden';
                        }

                        function isElementInViewport(el) {
                            const rect = el.getBoundingClientRect();
                            if (!rect) {
                                throw new Error("Element's bounding rect is null");
                            }
                            return (
                            rect.top >= 0 &&
                            rect.left >= 0 &&
                            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                            );
                        }

                        // Check if the element is visible style-wise
                        if (!isStyleVisible(el)) {
                            return false;
                        }

                        // Traverse up the DOM and check if any ancestor element is hidden
                        let parent = el;
                        while (parent) {
                            if (!isStyleVisible(parent)) {
                                return false;
                            }
                            parent = parent.parentElement;
                        }

                        // Finally, check if the element is within the viewport
                        return isElementInViewport(el);
                    }

                    if (e) {
                        e.style.border = "1px solid red";

                        const position = e.getBoundingClientRect();

                        if (position.width > 5 && position.height > 5 && isElementVisible(e)) {
                            const link_text = e.textContent.replace(/[^a-zA-Z0-9 ]/g, '');
                            e.setAttribute( "gemini-link-text", link_text );
                        }
                    }
                }, e);
            } catch (e) {
                console.error("highlight_links: Exception while highlighting link: " + e);
            }
        } );
    } catch (e) {
        console.error("highlight_links: Exception while getting links: " + e);
    }
	await sleep(1000);
	console.error('Links highlighted')
}

async function waitForEvent(page, event) {
    return page.evaluate(event => {
        return new Promise((r, _) => {
            document.addEventListener(event, function(e) {
                r();
            });
        });
    }, event)
}


// Launch browser
const launchBrowser = async () => {
    const browser = await puppeteer.launch( {
        headless: "false",
        args: ['--no-sandbox'],
    } );
	return browser;
};

// Initialize browser page
const initPage = async (browser) => {
    const page = await browser.newPage();
    await page.setViewport(
		{
			width: 1200,
			height: 1200,
			deviceScaleFactor: 1
		}
	);
    return page;
};

const init_model = async (model_name, safetySettings) => {
	const model = genAI.getGenerativeModel({ model: model_name, safetySettings });
	const messages = model.startChat({
        history: [
			{
				role: "user",
				parts: [{ text: prompt_template }]
			},
			{
				role: 'model',
				parts: [{ text: 'How can I assist you today?' }]
			}],
        generationConfig: { maxOutputTokens: 8192 },
    });
	return { model, messages };
}

// Ask user for input
const user_input = async (message) => {
	sendMessageToPython('Gemini:', message)
	return await receiveMessageFromPython();
}

// Handle url statement
const url_state = async (url, page) => {
	console.error("Crawling " + url);
	await page.goto( url, {
		waitUntil: "domcontentloaded",
		timeout: timeout,
	} );

	await Promise.race( [
		waitForEvent(page, 'load'),
		sleep(timeout)
	] );

	await highlight_links( page );

	await page.screenshot( {
		path: "screenshot.jpg",
		fullPage: true,
	} );
	url = null;

	return [url, true];
}

// Handle screenshot statement
const screenshot_state = async (msg) => {
	const base64_image = await image_to_base64("screenshot.jpg", "image/jpeg");
	msg.push(base64_image);
	msg.push(click_prompt_template);
	
	return [msg, base64_image, false];
}

// Handle model response
const ask_model = async (msg, messages) => {
	const result = await messages.sendMessage(msg);
	const response = await result.response;
	return [response.text(), messages];
}

// Handle url and screenshot statements
const url_screenshot_state = async (url, screenshot_taken, msg, base64_image, page) => {
	if( url ) {
		[url, screenshot_taken] = await url_state(url, page);
	}
	if( screenshot_taken ) {
		[msg, base64_image, screenshot_taken] = await screenshot_state(msg);
	}

	return [url, screenshot_taken, msg, base64_image];
}

// Find elements loop
const find_elements = async (elements, link_text) => {
    let exact = null;
    let partial = null;

    for (const element of elements) {
        try {
            const textContent = await element.evaluate(el => el.textContent);

            if (textContent.includes(link_text)) {
                partial = element;
            }
            if (textContent === link_text) {
                exact = element;
            }
        } catch (e) {
            console.error("ERROR: Exception while finding elements", e.message);
        }
    }

    return [exact, partial];
}

// Exact and partial statement
const exact_and_partial_statement = async (exact, partial, page) => {
    if (exact) {
        elementToClick = exact;
    } else if (partial) {
        elementToClick = partial;
    } else {
        msg.push("ERROR: I was unable to find the link");
        return;
    }

    const [response] = await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded' }).catch(e => console.error("Navigation timeout/error:", e.message)),
        elementToClick.click()
    ]);

	await Promise.race( [
		waitForEvent(page, 'load'),
		sleep(timeout)
	] );

	await highlight_links(page);

	await page.screenshot({
		path: "screenshot.jpg",
		quality: 100,
		fullpage: true
	});

	return response;
}

(async () => {
	const browser = await launchBrowser();
    const page = await initPage(browser);
	
	let {model, messages} = await init_model(model_name, safetySettings);

    prompt = process.argv[2];
	msg = [];
    msg.push(prompt);
	
    let url;
	let base64_image = null;
    let screenshot_taken = false;
	let message_text = null;

    while( true ) {
		
		[url, screenshot_taken, msg, base64_image] = await url_screenshot_state(url, screenshot_taken, msg, base64_image, page);

		await sleep(SLEEP_TIME / 2);
        [message_text, messages] = await ask_model(msg, messages);
		msg.push("Gemini: " + message_text);
        console.error("Gemini: " + message_text);
		
		const regex = /{"click":\s*"([^"]+)"}/;
		const match = message_text.match(regex);
		if (match) {
			await sleep(SLEEP_TIME / 2);
			const link_text = match[1];
        
            try {
                const elements = await page.$$('[gemini-link-text]');
        
                let partial;
                let exact;
        
				[exact, partial] = await find_elements(elements, link_text);
        
                if (exact || partial) {
					response = await exact_and_partial_statement(exact, partial, page);
					screenshot_taken = true;
                }
				else {
                    throw new Error("Can't find link");
                }
            } catch (error) {
                console.error("ERROR: Clicking failed", error);
			
                msg.push("ERROR: I was unable to click that element");
            }

            continue;
        } else if (message_text.match(urlRegex)) {
            let parts = message_text.match(urlRegex);
            url = parts[1];
        
            continue;
        } else {
            console.log(message_text);
        }

        process.exit(0);
    }
})();