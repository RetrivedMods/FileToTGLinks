const express = require('express');
const app = express();
const PORT = process.env.PORT || 8000;

app.get('/', (req, res) => res.send('Bot is alive!'));

app.listen(PORT, () => {
  console.log(`Dummy server running on port ${PORT}`);
});

