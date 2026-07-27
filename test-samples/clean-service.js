// FIXTURE — negative control. This file is CORRECT.
// Expect: no findings. If the agent flags anything here, it is a false positive.

const { pool } = require('../db');

// Parameterized, scoped to the authenticated user, and paginated.
async function listOrders(userId, { limit = 20, offset = 0 } = {}) {
  const { rows } = await pool.query(
    `SELECT id, total, created_at
       FROM orders
      WHERE user_id = $1
      ORDER BY created_at DESC
      LIMIT $2 OFFSET $3`,
    [userId, limit, offset]
  );
  return rows;
}

async function getOrder(orderId, userId) {
  const { rows } = await pool.query(
    'SELECT id, total FROM orders WHERE id = $1 AND user_id = $2',
    [orderId, userId]
  );
  return rows[0] || null;
}

module.exports = { listOrders, getOrder };
