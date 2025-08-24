// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const { Pool } = require('pg');
const morgan = require('morgan');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' }});

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// ---------- DB ----------
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://malume:malume_pw@localhost:5432/malume_nico'
});

// Helpers
const RANDS = (cents) => `R${(cents/100).toFixed(0)}`; // you use whole rands
const FREE_DELIVERY_THRESHOLD = 28000; // R280 in cents
const DEFAULT_DELIVERY_FEE = 2000;     // R20 fallback if not free

function computeTotals(items) {
  const subtotal = items.reduce((s, it) => s + it.unit_price_cents * it.qty, 0);
  const free = subtotal >= FREE_DELIVERY_THRESHOLD;
  const delivery = free ? 0 : DEFAULT_DELIVERY_FEE;
  const total = subtotal + delivery;
  return { subtotal, free, delivery, total };
}

// ---------- SOCKET.IO ----------
io.on('connection', (socket) => {
  // Clients can join rooms: order:<id> or table:<tableNumber>
  socket.on('join', ({ orderId, tableNumber }) => {
    if (orderId) socket.join(`order:${orderId}`);
    if (tableNumber) socket.join(`table:${tableNumber}`);
  });
});

// Emit helpers
function emitOrderUpdate(orderId, payload) {
  io.to(`order:${orderId}`).emit('order:update', payload);
}
function emitNewOrderTable(tableNumber, payload) {
  if (!tableNumber) return;
  io.to(`table:${tableNumber}`).emit('order:new', payload);
}

// ---------- ROUTES ----------

// Health
app.get('/api/health', (_req, res) => res.json({ ok: true }));

// Menu
app.get('/api/menu', async (_req, res) => {
  const { rows } = await pool.query('SELECT id,name,price_cents,img_url FROM menu_items WHERE is_active=true ORDER BY id');
  res.json(rows);
});

// Create Order (empty)
app.post('/api/orders', async (req, res) => {
  try {
    const { type, tableNumber, phone, email } = req.body;

    if (type === 'DINE_IN' && !tableNumber) {
      return res.status(400).json({ error: 'tableNumber required for DINE_IN' });
    }
    if (type === 'DELIVERY' && (!phone || !email)) {
      return res.status(400).json({ error: 'phone and email required for DELIVERY' });
    }

    const insert = `
      INSERT INTO orders (type, table_number, phone, email)
      VALUES ($1,$2,$3,$4)
      RETURNING *;
    `;
    const { rows } = await pool.query(insert, [type, tableNumber || null, phone || null, email || null]);

    const order = rows[0];
    emitNewOrderTable(order.table_number, { orderId: order.id, status: order.status });
    res.status(201).json(order);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'failed to create order' });
  }
});

// Add/Update items (upsert pattern: replace all items)
app.put('/api/orders/:id/items', async (req, res) => {
  const client = await pool.connect();
  try {
    const orderId = req.params.id;
    const items = req.body.items || []; // [{menu_item_id, qty}]

    await client.query('BEGIN');

    // fetch menu for pricing
    const menuMap = new Map();
    const { rows: menuRows } = await client.query('SELECT id,name,price_cents FROM menu_items WHERE is_active=true');
    menuRows.forEach(r => menuMap.set(r.id, r));

    // clear existing items
    await client.query('DELETE FROM order_items WHERE order_id=$1', [orderId]);

    // insert new
    const toInsert = [];
    for (const it of items) {
      const m = menuMap.get(it.menu_item_id);
      if (!m) continue;
      const qty = Math.max(1, parseInt(it.qty, 10));
      const line = m.price_cents * qty;
      toInsert.push({
        order_id: orderId,
        menu_item_id: m.id,
        name: m.name,
        unit_price_cents: m.price_cents,
        qty,
        line_total_cents: line
      });
    }

    for (const row of toInsert) {
      await client.query(
        `INSERT INTO order_items
        (order_id, menu_item_id, name, unit_price_cents, qty, line_total_cents)
        VALUES ($1,$2,$3,$4,$5,$6)`,
        [row.order_id, row.menu_item_id, row.name, row.unit_price_cents, row.qty, row.line_total_cents]
      );
    }

    // recompute totals
    const { rows: itemsRows } = await client.query('SELECT unit_price_cents, qty FROM order_items WHERE order_id=$1', [orderId]);
    const totals = computeTotals(itemsRows.map(r => ({ unit_price_cents: r.unit_price_cents, qty: r.qty })));

    await client.query(
      `UPDATE orders SET
        subtotal_cents=$1,
        delivery_fee_cents=$2,
        total_cents=$3,
        free_delivery=$4,
        updated_at=NOW()
      WHERE id=$5`,
      [totals.subtotal, totals.delivery, totals.total, totals.free, orderId]
    );

    await client.query('INSERT INTO order_events (order_id, event, meta) VALUES ($1,$2,$3)',
      [orderId, 'ITEMS_UPDATED', JSON.stringify({ items })]);

    await client.query('COMMIT');

    // fetch full order to return
    const { rows: orderRows } = await pool.query('SELECT * FROM orders WHERE id=$1', [orderId]);
    const { rows: oi } = await pool.query('SELECT * FROM order_items WHERE order_id=$1', [orderId]);

    const payload = { order: orderRows[0], items: oi };
    emitOrderUpdate(orderId, payload);

    res.json(payload);
  } catch (e) {
    await pool.query('ROLLBACK');
    console.error(e);
    res.status(500).json({ error: 'failed to update items' });
  } finally {
    client.release();
  }
});

// Get order (with items)
app.get('/api/orders/:id', async (req, res) => {
  const orderId = req.params.id;
  const { rows: o } = await pool.query('SELECT * FROM orders WHERE id=$1', [orderId]);
  if (!o[0]) return res.status(404).json({ error: 'not found' });
  const { rows: items } = await pool.query('SELECT * FROM order_items WHERE order_id=$1', [orderId]);
  res.json({ order: o[0], items });
});

// Update status (for staff/KDS)
app.patch('/api/orders/:id/status', async (req, res) => {
  const orderId = req.params.id;
  const { status } = req.body; // PENDING|CONFIRMED|IN_KITCHEN|READY|COMPLETED|CANCELLED
  const { rows } = await pool.query(
    'UPDATE orders SET status=$1, updated_at=NOW() WHERE id=$2 RETURNING *',
    [status, orderId]
  );
  if (!rows[0]) return res.status(404).json({ error: 'not found' });

  await pool.query('INSERT INTO order_events (order_id, event, meta) VALUES ($1,$2,$3)',
    [orderId, 'STATUS_CHANGED', JSON.stringify({ status })]);

  emitOrderUpdate(orderId, { order: rows[0] });
  res.json(rows[0]);
});

// Simple totals preview (optional)
app.post('/api/price', async (req, res) => {
  const items = req.body.items || [];
  // fetch menu
  const { rows: menu } = await pool.query('SELECT id, price_cents FROM menu_items WHERE is_active=true');
  const map = new Map(menu.map(m => [m.id, m.price_cents]));
  const collapsed = items.map(i => ({ unit_price_cents: map.get(i.menu_item_id) || 0, qty: i.qty || 1 }));
  const totals = computeTotals(collapsed);
  res.json(totals);
});

// ---------- START ----------
const PORT = process.env.PORT || 4000;
server.listen(PORT, () => console.log(`API + Socket.IO running on :${PORT}`));
