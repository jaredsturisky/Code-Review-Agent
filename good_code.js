const express = require('express');
const mysql = require('mysql2/promise');

const router = express.Router();

// Secrets come from the environment, never hardcoded.
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 10,
});

// Look up a user by id using a parameterized query, with validation,
// pagination-free single-record access, and centralized error handling.
router.get('/users/:id', async (req, res, next) => {
  const userId = Number(req.params.id);

  if (!Number.isInteger(userId) || userId <= 0) {
    return res.status(400).json({ error: 'A valid numeric user id is required.' });
  }

  try {
    const [rows] = await pool.execute(
      'SELECT id, name, email FROM users WHERE id = ? LIMIT 1',
      [userId]
    );

    if (rows.length === 0) {
      return res.status(404).json({ error: 'User not found.' });
    }

    return res.status(200).json(rows[0]);
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
