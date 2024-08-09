// server.js
const express = require('express');
const bodyParser = require('body-parser');
const callLlama = require('./call_llama');  
const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static('public')); // Serve static files from the 'public' directory

app.post('/api/chat', async (req, res) => {
    const userMessage = req.body.question;
    
    try {
        const answer = await callLlama(userMessage);
        res.json({ answer });
    } catch (error) {
        console.error('Error handling the chat request:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});

