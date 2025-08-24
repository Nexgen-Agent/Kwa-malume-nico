-- schema.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Menu
CREATE TABLE menu_items (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  img_url TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tables in venue (for QR)
CREATE TABLE venue_tables (
  id SERIAL PRIMARY KEY,
  table_number TEXT UNIQUE NOT NULL, -- e.g. "A12"
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Orders
CREATE TYPE order_type AS ENUM ('DINE_IN', 'DELIVERY');
CREATE TYPE order_status AS ENUM ('PENDING','CONFIRMED','IN_KITCHEN','READY','COMPLETED','CANCELLED');

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  type order_type NOT NULL,
  status order_status NOT NULL DEFAULT 'PENDING',
  table_number TEXT,                 -- required for DINE_IN
  phone TEXT,                        -- required for DELIVERY
  email TEXT,                        -- required for DELIVERY
  subtotal_cents INTEGER NOT NULL DEFAULT 0,
  delivery_fee_cents INTEGER NOT NULL DEFAULT 0,
  total_cents INTEGER NOT NULL DEFAULT 0,
  free_delivery BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  menu_item_id INTEGER NOT NULL REFERENCES menu_items(id),
  name TEXT NOT NULL,
  unit_price_cents INTEGER NOT NULL,
  qty INTEGER NOT NULL CHECK (qty > 0),
  line_total_cents INTEGER NOT NULL
);

-- Optional: audit trail for order progress
CREATE TABLE order_events (
  id SERIAL PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  meta JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Seed menu (match your assets 1..10)
INSERT INTO menu_items (name, price_cents, img_url) VALUES
('Titanic Family Kota', 10000, 'assets/img/menu/1.jpg'),
('Danked Wings',        7500, 'assets/img/menu/2.jpg'),
('Bugatti Kota',        6000, 'assets/img/menu/3.jpg'),
('Burger',              6000, 'assets/img/menu/4.jpg'),
('Range Rover Kota',    5000, 'assets/img/menu/5.jpg'),
('Dagwood',             4500, 'assets/img/menu/6.jpg'),
('BMW M4 Kota',         4000, 'assets/img/menu/7.jpg'),
('Dessert',             4000, 'assets/img/menu/8.jpg'),
('Omoda Kota',          3500, 'assets/img/menu/9.jpg'),
('Haval Kota',          3000, 'assets/img/menu/10.jpg');