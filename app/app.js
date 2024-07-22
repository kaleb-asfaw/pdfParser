// app.js
const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const bcrypt = require('bcrypt');
const { findPasswordSalt } = require('./db');
const { prepare } = require('./prepare');

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Prepare the database
prepare();

app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    
    try {
        const user = await findPasswordSalt(email);
        if (user && await bcrypt.compare(password, user.pwdhash)) {
            res.redirect('/dashboard');
        } else {
            res.status(401).send('Invalid credentials');
        }
    } catch (error) {
        res.status(500).send('Internal Server Error');
    }
});

app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
