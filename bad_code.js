const express = require('express');
const { exec } = require('child_process');
const mysql = require('mysql');
const fs = require('fs');

const app = express();

const DB_PASSWORD = "root_password_123";
const JWT_SECRET = "hardcoded-super-secret-key";

const db = mysql.createConnection({
  host: 'localhost',
  user: 'admin',
  password: DB_PASSWORD,
  database: 'app'
});

// SQL injection: user input concatenated straight into the query
app.get('/users', (req, res) => {
  const query = "SELECT * FROM users WHERE name = '" + req.query.name + "'";
  db.query(query, (err, rows) => {
    res.send(rows);
  });
});

// Command injection: unsanitized input passed to a shell
app.get('/lookup', (req, res) => {
  exec('nslookup ' + req.query.domain, (err, stdout) => {
    res.send(stdout);
  });
});

// Path traversal + no error handling on missing file
app.get('/download', (req, res) => {
  const data = fs.readFileSync('./files/' + req.query.file);
  res.send(data);
});

// eval on user input
app.get('/eval', (req, res) => {
  res.send('' + eval(req.query.expr));
});

// Secret leaked into logs, no auth check on a sensitive route
app.get('/admin/token', (req, res) => {
  console.log('Issuing token with secret ' + JWT_SECRET);
  res.send(JWT_SECRET);
});

// Swallowed error, no status code
app.post('/save', (req, res) => {
  try {
    db.query('INSERT INTO logs SET ?', req.body);
  } catch (e) {}
  res.send('ok');
});

app.listen(3000, () => {
  console.log('Server up on 3000, db password is ' + DB_PASSWORD);
});
