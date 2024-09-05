const fetch = require('node-fetch');
const https = require('https');

// Create an HTTPS agent that bypasses SSL verification
const agent = new https.Agent({
    rejectUnauthorized: false
});

async function callLlama(userMessage) {
    const host = "https://ec2-35-95-160-121.us-west-2.compute.amazonaws.com/v1/chat/completions";
    const openai_api_key = "EMPTY";

    const headers = {
        "Authorization": `Bearer ${openai_api_key}`,
        "Content-Type": "application/json"
    };

    const data = {
        "model": "meta-llama/Llama-2-7b-chat-hf",
        "messages": [
            {"role": "system", "content": "You're a helpful NASA assistant named Astro. Speak professionally, don't emote and be nice."},
            {"role": "user", "content": userMessage}
        ]
    };

    try {
        const response = await fetch(host, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(data),
            agent: agent  // Use the custom HTTPS agent to bypass SSL verification
        });

        if (response.ok) {
            const chatResponse = await response.json();
            return chatResponse['choices'][0]['message']['content'];
        } else {
            console.error(`Error: ${response.status}`);
            console.error(await response.text());
            return "Sorry, there was an error processing your request.";
        }
    } catch (error) {
        console.error('Error:', error);
        return "Sorry, there was an error processing your request.";
    }
}

module.exports = callLlama;
