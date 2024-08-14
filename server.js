const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static('public'));

app.post('/api/chat/', async (req, res) => {
    console.log('Request Body:', req.body);  // Log the request body to ensure sessionId is included
    const userMessage = req.body.message;
    const sessionId = req.body.sessionId;

    if (!userMessage || !sessionId) {
        console.log('Missing message or sessionId');
        return res.status(400).json({ error: 'Missing message or sessionId' });
    }

    try {
        const response = await axios.post('http://localhost:8000/chat/', {
            message: userMessage,
            sessionId: sessionId
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        res.json({ response: response.data.response });
    } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});
