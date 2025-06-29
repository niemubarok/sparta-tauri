const express = require('express');
const path = require('path');
const router = express.Router();

// Serve main application page
router.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
});

// Serve settings page
router.get('/settings', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'settings.html'));
});

// Serve test page (development only)
router.get('/test', (req, res) => {
  if (process.env.NODE_ENV !== 'development') {
    return res.status(404).send('Page not found');
  }
  res.sendFile(path.join(__dirname, '..', 'public', 'test.html'));
});

module.exports = router;
