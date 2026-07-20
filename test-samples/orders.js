const { Order } = require('../models');

// IDOR: fetch by id without owner scope (DB-002 -> warning, advisory)
async function getOrder(req, res) {
  const order = await Order.findByPk(req.params.id);
  if (!order) {
    return res.status(404).json({ error: 'Not found' });
  }
  return res.json(order);
}

// Unbounded query (DB-003 -> warning)
async function listOrders(req, res) {
  try {
    const orders = await Order.findAll();
    return res.json(orders);
  } catch (err) {
    // Stack trace leaked to client (NODE-005 -> warning)
    return res.status(500).json({ error: err.stack });
  }
}

module.exports = { getOrder, listOrders };
